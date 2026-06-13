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
    ]
}}

## 约束
1. 每个字段都必须填写，不可省略；文档确实未提及的字段写「文档未提及」
2. 描述要具体可理解，不要照搬文档原文的模糊表述
3. 业务规则要尽量提取具体的约束条件（字段长度、格式要求、必填/选填）
4. 模块划分要合理，不要过细或过粗，通常按系统菜单或功能域划分
5. 优先级根据业务重要性判断：核心流程为「高」，辅助功能为「中」，边缘功能为「低」
6. 只输出 JSON，不要有其他文字"""

# ============ Stage 2: 测试用例生成 ============

STAGE_2_CASES = """你是专业的测试用例生成器。根据以下功能点生成结构化测试用例。

## 项目前缀
{project_prefix}

## 模块列表及缩写
{module_list}

## 功能点
{feature_points}

## 生成规则
1. 为每个功能点生成至少 1 条测试用例
2. 覆盖范围要求：
   - 正向流程：核心业务操作能正确完成
   - 基础操作：页面进入、数据加载、基本交互
   - 边界值：最大值、最小值、空值、超长输入
   - 异常场景：数据缺失、服务不可用、操作异常、配置缺失
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

## 生成规则
1. 只为上面列出的变更功能点生成用例，不要生成其他功能点的用例
2. 重点覆盖变更带来的新增/变化场景：新增功能的正向流程、修改点影响的边界与异常
3. 避免与基线用例重复：标题和步骤应体现本次变更的差异点
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


def build_stage2_prompt(
    project_prefix: str,
    modules: list[dict],
    feature_points: list[dict],
) -> str:
    """
    构建 Stage 2 测试用例生成 Prompt

    Args:
        project_prefix: 项目前缀，如 "SPD"
        modules: 模块列表 [{"name": "数据整合", "code": "SJZH"}, ...]
        feature_points: 功能点列表 [{"name": "...", "module_name": "数据整合", ...}, ...]
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
    )


def build_stage2_incremental_prompt(
    project_prefix: str,
    modules: list[dict],
    feature_points: list[dict],
    change_context: str = "",
) -> str:
    """
    构建 Stage 2 增量测试用例生成 Prompt。

    与全量版区别：明确要求只为「变更功能点」补充用例，避免重复覆盖基线。

    Args:
        project_prefix: 项目前缀，如 "SPD"
        modules: 模块列表 [{"name": "...", "code": "..."}, ...]
        feature_points: 变更功能点列表（结构与全量版一致）
        change_context: 变更摘要文本，说明各功能点是新增/修改
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
    )

