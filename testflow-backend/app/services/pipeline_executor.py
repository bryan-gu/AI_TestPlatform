"""
流水线真实执行引擎（SKILL 对齐版）

复现 SKILL bf-test-workflow 的核心流程：
  Stage 1: 需求分析 — 解析文档，提取模块+功能点 → 写入 DB + 文件（对齐 SKILL A1）
  Stage 2: 测试用例生成 — 基于功能点生成结构化用例 → 写入 DB + Excel（对齐 SKILL P1）
  Stage 3: E2E 脚本生成 — 占位（Phase B 实现）
  Stage 4: 执行与自愈 — 占位（Phase C 实现）

使用方式（在 BackgroundTask 中运行）：
    executor = PipelineExecutor()
    background_tasks.add_task(executor.execute, execution_id)
"""

import json
import re
import logging
from datetime import datetime

from sqlalchemy.orm import joinedload

from app.core.database import SessionLocal
from app.models.pipeline import PipelineExecution, PipelineStage
from app.models.document import Document
from app.models.module import Module
from app.models.feature_point import FeaturePoint
from app.models.testcase import TestCase
from app.models.project import Project
from app.services.llm_adapter import LLMAdapter
from app.services.llm_providers import LLMCallError
from app.services.artifact_manager import ArtifactManager
from app.services.prompts.skill_prompts import build_stage1_prompt, build_stage2_prompt

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """流水线执行引擎（SKILL 对齐版）"""

    def execute(self, execution_id: int):
        """
        执行流水线（在 BackgroundTask 中运行）
        使用独立 Session，不依赖请求级 Session
        """
        db = SessionLocal()
        try:
            execution = self._get_execution(db, execution_id)
            if not execution:
                logger.error(f"Execution {execution_id} not found")
                return

            execution.status = "running"
            if not execution.started_at:
                execution.started_at = datetime.utcnow()
            db.commit()

            # 收集 Sprint 文档内容（Stage 1 的输入）
            document_content = self._collect_documents(db, execution)

            prev_result = None
            for stage in sorted(execution.stages, key=lambda s: s.stage_no):
                if stage.status == "completed":
                    continue
                try:
                    prev_result = self._execute_stage(
                        db, execution, stage,
                        prev_result=prev_result,
                        document_content=document_content,
                    )
                except Exception as e:
                    logger.exception(f"Stage {stage.stage_no} failed: {e}")
                    stage.status = "failed"
                    stage.result_summary = {"error": str(e)}
                    if not stage.started_at:
                        stage.started_at = datetime.utcnow()
                    stage.completed_at = datetime.utcnow()
                    execution.status = "failed"
                    execution.completed_at = datetime.utcnow()
                    self._calc_total_duration(execution)
                    db.commit()
                    return

            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            self._calc_total_duration(execution)
            db.commit()

        except Exception as e:
            logger.exception(f"Pipeline execution failed: {e}")
            try:
                execution = self._get_execution(db, execution_id)
                if execution and execution.status == "running":
                    execution.status = "failed"
                    execution.completed_at = datetime.utcnow()
                    db.commit()
            except Exception:
                pass
        finally:
            db.close()

    # ============ 阶段执行 ============

    def _execute_stage(self, db, execution, stage, *,
                       prev_result=None, document_content=""):
        """执行单个阶段，根据 stage_no 分发到具体处理逻辑"""
        stage.status = "running"
        stage.started_at = datetime.utcnow()
        db.commit()

        if stage.stage_no == 1:
            result = self._execute_stage_1(db, execution, stage, document_content)
        elif stage.stage_no == 2:
            result = self._execute_stage_2(db, execution, stage)
        elif stage.stage_no == 3:
            result = self._execute_stage_placeholder(db, execution, stage,
                "E2E 脚本生成将在 Phase B 实现。当前阶段跳过，等待浏览器集成。")
        elif stage.stage_no == 4:
            result = self._execute_stage_placeholder(db, execution, stage,
                "执行与自愈将在 Phase C 实现。当前阶段跳过，等待 Node.js + Playwright 集成。")
        else:
            result = None

        return result

    # ============ Stage 1: 需求分析 ============

    def _execute_stage_1(self, db, execution, stage, document_content: str):
        """
        对齐 SKILL A1: 文档解析 + 模块识别 + 功能点提取

        流程：
        1. 构建 Prompt（SKILL 对齐）
        2. 调用 LLM 获取结构化 JSON
        3. 解析结果 → 写入 Module 表 + FeaturePoint 表
        4. 生成功能点.md 文件 → 存为 Document 记录
        5. 更新 Stage 结果摘要
        """
        # 1. 构建 Prompt
        prompt = build_stage1_prompt(document_content)

        # 2. 调用 LLM
        adapter = LLMAdapter(db)
        result = adapter.call("需求文档分析", prompt)
        content = result["content"]

        # 3. 解析 JSON 结果
        parsed = self._extract_and_parse_json(content)
        if not parsed or "modules" not in parsed:
            preview = content[:500] if content else "(空)"
            raise ValueError(
                f"LLM 返回结果无法解析为有效的模块结构。原始返回前500字符: {preview}"
            )

        modules_data = parsed["modules"]
        project_id = execution.project_id

        # 4. 写入 Module + FeaturePoint + 文件
        module_count = 0
        feature_count = 0
        artifact_mgr = ArtifactManager(db, execution.sprint_id) if execution.sprint_id else None

        source_doc_id = self._get_first_doc_id(db, execution)
        source_doc_names = self._get_source_doc_names(db, execution)

        for mod_data in modules_data:
            mod_name = mod_data.get("name", "未命名模块")
            mod_code = mod_data.get("code", "")
            features_data = mod_data.get("features", [])

            # 写入 Module 表（get or create）
            module = self._get_or_create_module(db, project_id, mod_name, mod_code)
            module_count += 1

            # 生成功能点.md 内容
            md_lines = [f"# {mod_name} 功能点\n"]

            for feat_data in features_data:
                feat_name = feat_data.get("name", "未命名功能点")

                # 写入 FeaturePoint 表
                fp = FeaturePoint(
                    name=feat_name,
                    sprint_id=execution.sprint_id,
                    module_id=module.id,
                    source_doc_id=source_doc_id,
                )
                db.add(fp)
                feature_count += 1

                # 拼接 Markdown
                md_lines.append(f"\n## 功能点：{feat_name}\n")
                md_lines.append(f"- **描述**：{feat_data.get('description', '文档未提及')}")
                md_lines.append(f"- **操作入口**：{feat_data.get('entry', '文档未提及')}")
                md_lines.append(f"- **交互元素**：{feat_data.get('elements', '文档未提及')}")
                md_lines.append(f"- **业务规则**：{feat_data.get('rules', '文档未提及')}")
                md_lines.append(f"- **优先级**：{feat_data.get('priority', '中')}")
                if source_doc_names:
                    md_lines.append(f"- **来源**：需求文档（{source_doc_names}）")

            # 保存功能点.md 文件
            if artifact_mgr:
                md_content = "\n".join(md_lines)
                artifact_mgr.save_feature_points_md(mod_name, md_content)

        db.commit()

        # 5. 更新 Stage 记录
        stage.status = "completed"
        stage.completed_at = datetime.utcnow()
        stage.model = result["model"]
        stage.input_tokens = result["input_tokens"]
        stage.output_tokens = result["output_tokens"]
        stage.duration_ms = int(
            (stage.completed_at - stage.started_at).total_seconds() * 1000
        )
        stage.result_summary = {
            "识别模块": module_count,
            "提取功能点": feature_count,
            "模块列表": [m.get("name", "") for m in modules_data],
        }
        db.commit()

        return json.dumps(parsed, ensure_ascii=False)

    # ============ Stage 2: 测试用例生成 ============

    def _execute_stage_2(self, db, execution, stage):
        """
        对齐 SKILL P1/bf-case-generator: 功能点 → 结构化测试用例

        流程：
        1. 从 DB 读取 Stage 1 提取的功能点和模块
        2. 获取项目前缀
        3. 构建 Prompt（SKILL 对齐）
        4. 调用 LLM 获取 cases.json
        5. 解析 → 写入 TestCase 表
        6. 生成 cases.json + Excel 文件
        """
        project_id = execution.project_id
        sprint_id = execution.sprint_id

        # 1. 读取功能点和模块
        feature_points = db.query(FeaturePoint).filter(
            FeaturePoint.sprint_id == sprint_id
        ).all() if sprint_id else []

        if not feature_points:
            raise ValueError("没有找到功能点数据，请先完成 Stage 1 需求分析")

        # 收集模块信息
        module_ids = list(set(fp.module_id for fp in feature_points if fp.module_id))
        modules = db.query(Module).filter(Module.id.in_(module_ids)).all() if module_ids else []
        module_map = {m.id: m for m in modules}

        # 2. 获取项目前缀
        project_prefix = ""
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project and project.case_prefix:
                project_prefix = project.case_prefix

        # 如果项目没有配置前缀，从全局配置读取
        if not project_prefix:
            from app.models.ai_config import AIGlobalConfig
            prefix_config = db.query(AIGlobalConfig).filter(
                AIGlobalConfig.key == "project_prefix"
            ).first()
            if prefix_config and prefix_config.value:
                project_prefix = prefix_config.value

        if not project_prefix:
            project_prefix = "TC"

        # 3. 构建 Prompt
        modules_for_prompt = [
            {"name": m.name, "code": m.code or ""}
            for m in modules
        ]
        fps_for_prompt = []
        for fp in feature_points:
            mod = module_map.get(fp.module_id)
            fps_for_prompt.append({
                "name": fp.name,
                "module_name": mod.name if mod else "默认模块",
            })

        prompt = build_stage2_prompt(
            project_prefix=project_prefix,
            modules=modules_for_prompt,
            feature_points=fps_for_prompt,
        )

        # 4. 调用 LLM
        adapter = LLMAdapter(db)
        result = adapter.call("测试用例生成", prompt)
        content = result["content"]

        # 5. 解析 JSON 结果
        cases_data = self._extract_and_parse_json(content)
        if not cases_data or not isinstance(cases_data, list):
            # 尝试从包装对象中提取
            if isinstance(cases_data, dict):
                # 尝试多种可能的 key
                for key in ("test_cases", "cases", "testCases", "data", "results", "items"):
                    if key in cases_data and isinstance(cases_data[key], list):
                        cases_data = cases_data[key]
                        break
                else:
                    # dict 中没有已知 key，尝试取第一个 list 类型的 value
                    for v in cases_data.values():
                        if isinstance(v, list):
                            cases_data = v
                            break
            if not isinstance(cases_data, list):
                # 记录原始返回内容便于排查
                preview = content[:500] if content else "(空)"
                logger.error(f"Stage 2 JSON 解析失败, LLM 原始返回: {preview}")
                raise ValueError(
                    f"LLM 返回结果无法解析为测试用例数组。原始返回前500字符: {preview}"
                )

        # 6. 写入 TestCase 表 + 文件
        case_count = 0
        cases_by_module = {}  # 用于 Excel 生成
        artifact_mgr = ArtifactManager(db, sprint_id) if sprint_id else None

        for case_data in cases_data:
            case_module_name = case_data.get("module", "")
            case_id_str = case_data.get("id", "")
            case_title = case_data.get("title", "")

            # 查找 module_id
            module_id = None
            for m in modules:
                if m.name == case_module_name or (m.code and m.code in case_id_str):
                    module_id = m.id
                    break

            # 写入 TestCase 表（用 LLM 给出的 ID）
            tc = TestCase(
                case_no=case_id_str or f"{project_prefix}_TC_XXX_{case_count + 1:03d}",
                title=case_title,
                priority=self._map_priority(case_data.get("priority", "")),
                exec_status="待执行",
                project_id=project_id,
                module_id=module_id,
                module=case_module_name,
                preconditions=case_data.get("precondition", ""),
                test_data=case_data.get("test_data", ""),
                test_steps=case_data.get("steps", ""),
                expected_result=case_data.get("expected", ""),
            )
            db.add(tc)
            case_count += 1

            # 按模块分组（用于 Excel）
            if case_module_name not in cases_by_module:
                cases_by_module[case_module_name] = []
            cases_by_module[case_module_name].append(case_data)

        db.commit()

        # 保存 cases.json 文件（每个模块一个）
        if artifact_mgr:
            for mod_name, mod_cases in cases_by_module.items():
                artifact_mgr.save_cases_json(mod_name, mod_cases)
            # 生成汇总 Excel
            artifact_mgr.save_excel(cases_by_module)

        # 7. 更新 Stage 记录
        stage.status = "completed"
        stage.completed_at = datetime.utcnow()
        stage.model = result["model"]
        stage.input_tokens = result["input_tokens"]
        stage.output_tokens = result["output_tokens"]
        stage.duration_ms = int(
            (stage.completed_at - stage.started_at).total_seconds() * 1000
        )

        # 生成摘要
        module_case_counts = {}
        for mod_name, mod_cases in cases_by_module.items():
            module_case_counts[mod_name] = len(mod_cases)

        stage.result_summary = {
            "生成用例": case_count,
            "覆盖模块": len(cases_by_module),
            "各模块用例数": module_case_counts,
        }
        db.commit()

        return json.dumps(cases_data, ensure_ascii=False)

    # ============ Stage 3/4: 占位（Phase B/C） ============

    def _execute_stage_placeholder(self, db, execution, stage, message: str):
        """占位阶段执行（Phase B/C 未实现前使用）"""
        stage.status = "completed"
        stage.completed_at = datetime.utcnow()
        stage.started_at = stage.started_at or datetime.utcnow()
        stage.duration_ms = 0
        stage.result_summary = {"说明": message, "状态": "已跳过（待后续阶段实现）"}
        db.commit()
        return message

    # ============ 辅助方法 ============

    def _get_execution(self, db, execution_id: int) -> PipelineExecution | None:
        return db.query(PipelineExecution).options(
            joinedload(PipelineExecution.stages),
        ).filter(PipelineExecution.id == execution_id).first()

    def _collect_documents(self, db, execution) -> str:
        """收集 Sprint 下所有文档内容作为 Stage 1 的输入"""
        if not execution.sprint_id:
            return ""

        documents = db.query(Document).filter(
            Document.sprint_id == execution.sprint_id
        ).all()

        if not documents:
            return ""

        parts = []
        for doc in documents:
            parts.append(f"### 文档：{doc.name}")
            # 优先使用 AI 摘要，其次使用内容预览
            content = doc.ai_summary or doc.content_preview or ""
            if content:
                parts.append(content)
            parts.append("")

        return "\n".join(parts)

    def _get_or_create_module(self, db, project_id: int | None,
                               name: str, code: str) -> Module:
        """获取或创建 Module"""
        # 先按项目+名称查找
        query = db.query(Module)
        if project_id:
            query = query.filter(Module.project_id == project_id)
        module = query.filter(Module.name == name).first()

        if module:
            # 更新 code（如果原来没有）
            if code and not module.code:
                module.code = code.strip().upper()
                db.commit()
            return module

        # 创建新 Module
        module = Module(
            name=name,
            code=code.strip().upper() if code else "",
            project_id=project_id,
            color="",
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        return module

    def _extract_and_parse_json(self, text: str) -> dict | list | None:
        """从 LLM 回复中提取并解析 JSON，支持截断修复"""
        json_str = self._extract_json(text)
        if json_str:
            # 第一次尝试：直接解析
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error: {e}")

            # 第二次尝试：移除尾随逗号
            try:
                fixed = re.sub(r',\s*([}\]])', r'\1', json_str)
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

            # 第三次尝试：截断修复 — 自动补全未闭合的括号
            try:
                repaired = self._repair_truncated_json(json_str)
                if repaired:
                    return json.loads(repaired)
            except json.JSONDecodeError as e2:
                logger.warning(f"JSON 截断修复后仍无法解析: {e2}")

        return None

    def _repair_truncated_json(self, json_str: str) -> str | None:
        """
        尝试修复被截断的 JSON（LLM 输出未完成的情况）。
        策略：从末尾找到最后一个完整的值，截断到那里，然后补全闭合括号。
        """
        # 先移除尾随逗号
        json_str = re.sub(r',\s*$', '', json_str.rstrip())

        # 统计未闭合的括号
        open_braces = 0    # {
        open_brackets = 0  # [
        in_string = False
        escape_next = False

        for ch in json_str:
            if escape_next:
                escape_next = False
                continue
            if ch == '\\' and in_string:
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == '{':
                open_braces += 1
            elif ch == '}':
                open_braces -= 1
            elif ch == '[':
                open_brackets += 1
            elif ch == ']':
                open_brackets -= 1

        if open_braces < 0 or open_brackets < 0:
            return None  # 括号计数异常，无法修复

        # 尝试从末尾截断到最后一个完整值的位置
        # 寻找最后一个完整的 "key": value 或 value 对
        repaired = json_str

        # 如果末尾在字符串中间，截断到最后一个完整的字符串
        if in_string:
            # 找到最后引号前的内容
            last_quote = json_str.rfind('"')
            if last_quote > 0:
                # 看这个引号前面是否是 key: 的模式
                before = json_str[:last_quote].rstrip()
                # 如果是冒号后面，说明 value 的字符串被截断了，用空字符串代替
                if before.endswith(':'):
                    repaired = before + ' ""'
                elif before.endswith(','):
                    repaired = before
                else:
                    repaired = before + '"'

        # 移除末尾不完整的内容（最后一个逗号之后的不完整键值对）
        # 找到最后一个完整值结束的位置
        # 策略：逐步从末尾尝试添加闭合括号
        repaired = repaired.rstrip().rstrip(',')

        # 补全闭合括号
        repaired += '}' * max(0, open_braces) + ']' * max(0, open_brackets)

        return repaired

    def _extract_json(self, text: str) -> str | None:
        """从文本中提取 JSON 块"""
        # 尝试匹配 ```json ... ``` 代码块
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 尝试匹配 [...] （数组优先，Stage 2 期望数组）
        match = re.search(r'(\[[\s\S]*\])', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 尝试匹配 { ... }
        match = re.search(r'(\{[\s\S]*\})', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 整段文本直接尝试解析
        text = text.strip()
        if text.startswith(('{', '[')):
            return text

        return None

    def _get_first_doc_id(self, db, execution) -> int | None:
        """获取 Sprint 下第一个文档 ID（用于 FeaturePoint.source_doc_id）"""
        if not execution.sprint_id:
            return None
        doc = db.query(Document).filter(
            Document.sprint_id == execution.sprint_id
        ).first()
        return doc.id if doc else None

    def _get_source_doc_names(self, db, execution) -> str:
        """获取 Sprint 下所有文档名称"""
        if not execution.sprint_id:
            return ""
        docs = db.query(Document).filter(
            Document.sprint_id == execution.sprint_id
        ).all()
        return "、".join(d.name for d in docs) if docs else ""

    def _map_priority(self, priority_str: str) -> str:
        """将 LLM 返回的优先级映射为平台标准值"""
        mapping = {
            "high": "高", "高": "高",
            "medium": "中", "中": "中",
            "low": "低", "低": "低",
        }
        return mapping.get(priority_str.lower() if priority_str else "", "中")

    def _calc_total_duration(self, execution):
        if execution.started_at and execution.completed_at:
            delta = execution.completed_at - execution.started_at
            execution.total_duration_ms = int(delta.total_seconds() * 1000)
