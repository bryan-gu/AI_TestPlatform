"""
SKILL 对齐的 Prompt 模板集合

每个 Prompt 对齐 SKILL bf-test-workflow.md 中的对应阶段：
  - STAGE_1_ANALYZE:  对齐 A1 文档解析 → 提取模块+功能点
  - STAGE_2_CASES:    对齐 P1/bf-case-generator → 生成结构化测试用例

设计原则：
  1. 输出严格 JSON 格式，方便后端解析入库
  2. 覆盖正向/异常/边界/集成场景
  3. 步骤与预期结果一一对应
  4. 用例 ID 格式：{前缀}_TC_{模块缩写}_{序号}
"""

# ============ Stage 1: 需求分析 ============

STAGE_1_ANALYZE = """你是一个专业的软件测试需求分析师。请分析以下需求文档内容，提取所有功能模块和功能点。

## 需求文档内容
{document_content}

## 输出要求
请以 JSON 格式输出分析结果，严格遵循以下结构：
{{
    "modules": [
        {{
            "name": "模块名称（简短，如'数据整合'、'用户认证'）",
            "code": "模块英文缩写（大写，如'SJZH'、'DL'，用于用例编号）",
            "features": [
                {{
                    "name": "功能点名称",
                    "description": "功能描述（用自己的话概括，不要照搬原文）",
                    "entry": "操作入口路径（如：点击左侧菜单「XX」 → 点击「新增」按钮；文档未提及则写「文档未提及」）",
                    "elements": "涉及的交互元素：表单字段、按钮、表格等（文档未提及则写「文档未提及」）",
                    "rules": "业务规则：必填项、数据格式、校验规则等约束（文档未提及则写「文档未提及」）",
                    "priority": "高/中/低"
                }}
            ]
        }}
    ],
    "module_dependencies": [
        {{
            "from_module": "源模块名称（必须与上面 modules 中的 name 一致）",
            "to_module": "目标模块名称（必须与上面 modules 中的 name 一致）",
            "relation_type": "depends_on|calls|data_flow（依赖/调用/数据流 三选一）",
            "description": "依赖关系说明，如「订单创建后扣减库存」"
        }}
    ]
}}

## 约束
1. 每个字段都必须填写，不可省略；文档确实未提及的字段写「文档未提及」
2. 描述要具体可理解，不要照搬文档原文的模糊表述
3. 业务规则要尽量提取具体的约束条件（字段长度、格式要求、必填/选填）
4. 模块划分要合理，不要过细或过粗，通常按系统菜单或功能域划分
5. 优先级根据业务重要性判断：核心流程为「高」，辅助功能为「中」，边缘功能为「低」
6. module_dependencies 只输出文档中**明确提到**的模块间依赖/调用/数据流关系，不要臆测；from_module/to_module 必须是上面 modules 里出现过的模块名；若无任何模块间关系，输出空数组 []
7. 只输出 JSON，不要有其他文字"""

# ============ Stage 2: 测试用例生成 ============

STAGE_2_CASES = """你是专业的测试用例生成器。根据以下功能点生成结构化测试用例。

## 项目前缀
{project_prefix}

## 模块列表及缩写
{module_list}

## 功能点
{feature_points}

## 关联上下文（来自知识图谱）
{case_context}

## 生成规则
1. 为每个功能点生成至少 1 条测试用例
2. 覆盖范围要求：
   - 正向流程：核心业务操作能正确完成
   - 基础操作：页面进入、数据加载、基本交互
   - 边界值：最大值、最小值、空值、超长输入
   - 异常场景：数据缺失、服务不可用、操作异常、配置缺失
   - 集成测试：若存在关联模块，针对模块间依赖/调用关系生成跨模块交互的用例
   - 接口校验：若相关接口涉及数据校验（必填/格式/权限），生成对应异常用例
3. 用例 ID 格式：{project_prefix}_TC_{{模块缩写}}_{{序号}}（序号从 001 开始，同一模块连续编号）
4. 测试步骤第一条**必须**是：1. 用户输入用户名、密码点击登录。
5. 测试步骤与预期结果**一一对应**，项数必须相同
6. 菜单名、按钮名、字段名等用「」包裹，不要使用双引号

## 输出 JSON 格式
[
    {{
        "id": "{project_prefix}_TC_XX_001",
        "module": "模块名",
        "title": "简明测试标题",
        "precondition": "1. 前置条件1；2. 前置条件2",
        "test_data": "具体测试数据，无则填「无」",
        "steps": "1. 用户输入用户名、密码点击登录。\\n2. 下一步操作。\\n3. 再下一步。",
        "expected": "1. 登录成功。\\n2. 预期结果2。\\n3. 预期结果3。"
    }}
]

## 注意事项
- 每条用例的步骤数量必须与预期结果数量严格相等
- 前置条件要具体可验证，不要写模糊描述
- 测试数据要给出具体值，不要写「正常数据」之类的泛指
- 用例文本中如需引用菜单名、按钮名、字段名等，使用「」包裹，**禁止使用双引号""**
- 参考已有用例避免重复（标题、步骤不雷同），可借鉴其断言思路
- 只输出 JSON 数组，不要有其他文字
- 每个模块的用例必须连续编号，不要跳号"""


# ============ Stage 2 增量: 测试用例生成（仅变更功能点） ============

STAGE_2_INCREMENTAL_CASES = """你是专业的测试用例生成器。当前处于增量模式：基线用例已存在，请**仅**为下列「新增/修改」的功能点补充测试用例，不要为基线中已覆盖的功能点重复生成用例。

## 项目前缀
{project_prefix}

## 模块列表及缩写
{module_list}

## 本次变更的功能点（仅这些需要补充用例）
{feature_points}

## 变更上下文
{change_context}

## 关联上下文（来自知识图谱）
{case_context}

## 生成规则
1. 只为上面列出的变更功能点生成用例，不要生成其他功能点的用例
2. 重点覆盖变更带来的新增/变化场景：新增功能的正向流程、修改点影响的边界与异常
3. 避免与基线及已有用例重复（标题、步骤不雷同）；若关联上下文存在依赖模块或相关接口，补充跨模块交互及接口校验用例
4. 用例 ID 格式：{project_prefix}_TC_{{模块缩写}}_{{序号}}（序号从 001 开始，同一模块连续编号）
5. 测试步骤第一条**必须**是：1. 用户输入用户名、密码点击登录。
6. 测试步骤与预期结果**一一对应**，项数必须相同
7. 菜单名、按钮名、字段名等用「」包裹，不要使用双引号

## 输出 JSON 格式
[
    {{
        "id": "{project_prefix}_TC_XX_001",
        "module": "模块名",
        "title": "简明测试标题（体现变更点）",
        "precondition": "1. 前置条件1；2. 前置条件2",
        "test_data": "具体测试数据，无则填「无」",
        "steps": "1. 用户输入用户名、密码点击登录。\\n2. 下一步操作。",
        "expected": "1. 登录成功。\\n2. 预期结果2。"
    }}
]

## 注意事项
- 若认为某变更功能点无需新增用例，可以不输出该功能点的用例
- 只输出 JSON 数组，不要有其他文字
- 每个模块的用例必须连续编号，不要跳号"""


# ============ 辅助函数 ============

def build_stage1_prompt(document_content: str) -> str:
    """构建 Stage 1 需求分析 Prompt"""
    return STAGE_1_ANALYZE.format(
        document_content=document_content or "（未找到相关文档，请基于通用测试分析方法进行分析）"
    )


def _format_case_context(case_context: dict | None) -> str:
    """把 case_context（关联模块/相关接口/已有用例）格式化为 prompt 段落文本。各段为空显示「暂无」。"""
    if not case_context:
        return "（暂无关联上下文）"

    def _fmt_modules(items):
        if not items:
            return "（暂无）"
        lines = []
        for m in items:
            feats = "、".join(m.get("features", [])) or "（无功能点）"
            rel = m.get("relations", "")
            prefix = f"{m.get('name', '')}（{rel}）" if rel else m.get("name", "")
            lines.append(f"- {prefix}：{feats}")
        return "\n".join(lines)

    def _fmt_apis(items):
        if not items:
            return "（暂无）"
        return "\n".join(f"- {a.get('method', '')} {a.get('path', '')} — {a.get('summary', '')}" for a in items)

    def _fmt_cases(items):
        if not items:
            return "（暂无）"
        return "\n".join(f"- {c.get('case_no', '')} {c.get('title', '')}" for c in items)

    return (
        f"### 关联模块\n{_fmt_modules(case_context.get('related_modules', []))}\n\n"
        f"### 相关接口\n{_fmt_apis(case_context.get('related_apis', []))}\n\n"
        f"### 已有用例（避免重复，可借鉴断言）\n{_fmt_cases(case_context.get('existing_cases', []))}"
    )


def build_stage2_prompt(
    project_prefix: str,
    modules: list[dict],
    feature_points: list[dict],
    case_context: dict | None = None,
) -> str:
    """
    构建 Stage 2 测试用例生成 Prompt

    Args:
        project_prefix: 项目前缀，如 "SPD"
        modules: 模块列表 [{"name": "数据整合", "code": "SJZH"}, ...]
        feature_points: 功能点列表 [{"name": "...", "module_name": "数据整合", ...}, ...]
        case_context: 关联上下文（来自知识图谱），含 related_modules/related_apis/existing_cases
    """
    # 模块列表格式化
    module_lines = []
    for m in modules:
        module_lines.append(f"- {m['name']} → {m.get('code', 'XX')}")
    module_list_str = "\n".join(module_lines) if module_lines else "- 默认模块 → DEF"

    # 功能点按模块分组格式化
    fp_by_module = {}
    for fp in feature_points:
        mod_name = fp.get("module_name", "默认模块")
        if mod_name not in fp_by_module:
            fp_by_module[mod_name] = []
        fp_by_module[mod_name].append(fp)

    fp_sections = []
    for mod_name, fps in fp_by_module.items():
        fp_items = []
        for fp in fps:
            fp_items.append(
                f"### {fp['name']}\n"
                f"- 描述：{fp.get('description', '文档未提及')}\n"
                f"- 操作入口：{fp.get('entry', '文档未提及')}\n"
                f"- 交互元素：{fp.get('elements', '文档未提及')}\n"
                f"- 业务规则：{fp.get('rules', '文档未提及')}\n"
                f"- 优先级：{fp.get('priority', '中')}"
            )
        fp_sections.append(f"#### 模块：{mod_name}\n" + "\n\n".join(fp_items))

    feature_points_str = "\n\n".join(fp_sections) if fp_sections else "（无功能点信息）"

    return STAGE_2_CASES.format(
        project_prefix=project_prefix or "TC",
        module_list=module_list_str,
        feature_points=feature_points_str,
        case_context=_format_case_context(case_context),
    )


def build_stage2_incremental_prompt(
    project_prefix: str,
    modules: list[dict],
    feature_points: list[dict],
    change_context: str = "",
    case_context: dict | None = None,
) -> str:
    """
    构建 Stage 2 增量测试用例生成 Prompt。

    与全量版区别：明确要求只为「变更功能点」补充用例，避免重复覆盖基线。

    Args:
        project_prefix: 项目前缀，如 "SPD"
        modules: 模块列表 [{"name": "...", "code": "..."}, ...]
        feature_points: 变更功能点列表（结构与全量版一致）
        change_context: 变更摘要文本，说明各功能点是新增/修改
        case_context: 关联上下文（来自知识图谱），含 related_modules/related_apis/existing_cases
    """
    module_lines = []
    for m in modules:
        module_lines.append(f"- {m['name']} → {m.get('code', 'XX')}")
    module_list_str = "\n".join(module_lines) if module_lines else "- 默认模块 → DEF"

    fp_by_module = {}
    for fp in feature_points:
        mod_name = fp.get("module_name", "默认模块")
        fp_by_module.setdefault(mod_name, []).append(fp)

    fp_sections = []
    for mod_name, fps in fp_by_module.items():
        fp_items = []
        for fp in fps:
            fp_items.append(
                f"### {fp['name']}（{fp.get('change_type', '变更')}）\n"
                f"- 描述：{fp.get('description', '文档未提及')}\n"
                f"- 操作入口：{fp.get('entry', '文档未提及')}\n"
                f"- 交互元素：{fp.get('elements', '文档未提及')}\n"
                f"- 业务规则：{fp.get('rules', '文档未提及')}\n"
                f"- 优先级：{fp.get('priority', '中')}"
            )
        fp_sections.append(f"#### 模块：{mod_name}\n" + "\n\n".join(fp_items))

    feature_points_str = "\n\n".join(fp_sections) if fp_sections else "（无变更功能点）"
    change_context_str = change_context or "（未提供具体变更描述，请基于功能点信息判断变更影响）"

    return STAGE_2_INCREMENTAL_CASES.format(
        project_prefix=project_prefix or "TC",
        module_list=module_list_str,
        feature_points=feature_points_str,
        change_context=change_context_str,
        case_context=_format_case_context(case_context),
    )


# ============ 接口-用例覆盖映射（增强项批次 6 子项 C） ============

API_COVERAGE_MAP = """你是测试覆盖分析专家。请判断下列测试用例是否覆盖（测试）下列接口。
"覆盖"指：用例的步骤、测试数据或预期结果涉及调用或验证该接口。

## 接口列表
{endpoints_json}

## 测试用例列表
{testcases_json}

## 输出要求
严格输出 JSON，结构如下：
{{
  "mappings": [
    {{ "testcase_id": <用例id>, "api_id": <接口id>, "confidence": <0-100整数>, "evidence": "<简短理由>" }}
  ]
}}

约束：
1. 只输出确定存在覆盖关系的结果（confidence >= 60）
2. testcase_id 和 api_id 必须来自上述列表中真实存在的 id
3. 若无任何覆盖关系，输出 {{ "mappings": [] }}
4. 只输出 JSON，不要任何其他文字"""


def build_api_coverage_prompt(endpoints: list[dict], testcases: list[dict]) -> str:
    """构建接口-用例覆盖映射 Prompt。"""
    import json
    return API_COVERAGE_MAP.format(
        endpoints_json=json.dumps(endpoints, ensure_ascii=False, indent=2),
        testcases_json=json.dumps(testcases, ensure_ascii=False, indent=2),
    )


# ============ PRD 变更识别（增强项批次 6 子项 A） ============

CHANGE_DETECTION = """你是需求变更分析专家。下面是某 Sprint 的需求文档内容，以及基线（sprint_all）已有的功能点列表。
请识别本次需求文档中相对基线**新增、修改或废弃**的功能点（规则结构化对比可能遗漏的语义级变更）。

## 当前 Sprint 需求文档
{prd_text}

## 基线功能点
{baseline_features}

## 输出要求
严格输出 JSON：
{{
  "changes": [
    {{ "title": "<变更标题>", "change_type": "added|modified|removed", "module_name": "<模块>", "description": "<变更说明>", "priority": "高|中|低" }}
  ]
}}

约束：
1. 只输出基线中不存在（新增）、语义明显变化（修改）或需求明确废弃（删除）的功能点
2. 不要重复基线已有的、未变化的功能点
3. 变更说明需基于需求文档原文，不要臆测
4. 无变更则输出 {{ "changes": [] }}
5. 只输出 JSON，不要任何其他文字"""


def build_change_detection_prompt(prd_text: str, baseline_features: str) -> str:
    """构建 PRD 变更识别 Prompt。"""
    return CHANGE_DETECTION.format(
        prd_text=prd_text or "（无需求文档内容）",
        baseline_features=baseline_features or "（基线暂无功能点）",
    )


# ============ 接口模块归属推断（P0.3） ============

API_MODULE_CLASSIFY = """你是接口归属分析专家。请判断下列每个接口属于哪个业务模块。

## 项目模块列表（接口必须归属到其中之一）
{modules_json}

## 待归属接口列表
{apis_json}

## 输出要求
严格输出 JSON：
{{
  "mappings": [
    {{ "api_id": <接口id>, "module_id": <模块id 或 null>, "confidence": <0-100整数>, "reason": "<简短理由>" }}
  ]
}}

约束：
1. module_id 必须来自上面的模块列表；若无法确定归属，module_id 输出 null
2. 判断依据：接口路径、摘要、tag 的语义与模块名称的匹配度
3. 每个 api_id 只输出一次，且必须来自上面的接口列表
4. 只输出 JSON，不要任何其他文字"""


def build_api_module_classify_prompt(modules: list[dict], apis: list[dict]) -> str:
    """构建接口模块归属推断 Prompt。"""
    import json
    return API_MODULE_CLASSIFY.format(
        modules_json=json.dumps(modules, ensure_ascii=False, indent=2),
        apis_json=json.dumps(apis, ensure_ascii=False, indent=2),
    )

