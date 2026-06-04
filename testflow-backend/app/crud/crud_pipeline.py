import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload

from app.models.pipeline import PipelineExecution, PipelineStage
from app.models.sprint import Sprint
from app.models.project import Project


# ── 4 阶段定义 ──

STAGE_DEFINITIONS = [
    {"stage_no": 1, "stage_name": "需求分析"},
    {"stage_no": 2, "stage_name": "测试用例生成"},
    {"stage_no": 3, "stage_name": "E2E 脚本生成"},
    {"stage_no": 4, "stage_name": "执行与自愈"},
]

# 模拟数据 — 每个 stage_no 对应可能的模型和 result_summary
SIMULATE_MODELS = {
    1: "GPT-4o",
    2: "Claude 3.5 Sonnet",
    3: "GPT-4o",
    4: "Claude 3.5 Sonnet",
}

SIMULATE_SUMMARIES = {
    1: {
        "功能点": random.randint(15, 35),
        "业务规则": random.randint(8, 25),
        "API 端点": random.randint(5, 18),
        "图谱关联": random.randint(6, 20),
    },
    2: {
        "生成用例": random.randint(30, 80),
        "正向用例": random.randint(15, 40),
        "异常用例": random.randint(8, 20),
        "边界用例": random.randint(5, 15),
    },
    3: {
        "生成脚本": random.randint(20, 60),
        "Playwright": random.randint(10, 30),
        "Selenium": random.randint(5, 15),
        "覆盖率": f"{random.randint(70, 95)}%",
    },
    4: {
        "执行用例": random.randint(20, 50),
        "通过": random.randint(15, 45),
        "失败": random.randint(1, 8),
        "自愈成功": random.randint(0, 5),
    },
}


# ── 查询 ──

def get_executions(db: Session, project_id: int | None = None) -> list[PipelineExecution]:
    query = db.query(PipelineExecution).options(joinedload(PipelineExecution.project), joinedload(PipelineExecution.sprint))
    if project_id:
        query = query.filter(PipelineExecution.project_id == project_id)
    return query.order_by(PipelineExecution.created_at.desc()).all()


def get_execution(db: Session, execution_id: int) -> PipelineExecution | None:
    return db.query(PipelineExecution).options(
        joinedload(PipelineExecution.project),
        joinedload(PipelineExecution.sprint),
        joinedload(PipelineExecution.stages),
    ).filter(PipelineExecution.id == execution_id).first()


# ── 创建 ──

def create_execution(db: Session, project_id: int | None = None, sprint_id: int | None = None, mode: str = "full") -> PipelineExecution:
    exec_obj = PipelineExecution(
        project_id=project_id,
        sprint_id=sprint_id,
        mode=mode,
        status="waiting",
    )
    db.add(exec_obj)
    db.flush()

    # 创建 4 个空 stage
    for defn in STAGE_DEFINITIONS:
        stage = PipelineStage(
            execution_id=exec_obj.id,
            stage_no=defn["stage_no"],
            stage_name=defn["stage_name"],
            status="waiting",
        )
        db.add(stage)

    db.commit()
    db.refresh(exec_obj)
    return exec_obj


# ── 暂停 ──

def pause_execution(db: Session, exec_obj: PipelineExecution) -> PipelineExecution:
    if exec_obj.status != "running":
        return exec_obj
    exec_obj.status = "paused"
    # 将当前 running 的 stage 也标记为 waiting（暂停）
    for stage in exec_obj.stages:
        if stage.status == "running":
            stage.status = "waiting"
    db.commit()
    db.refresh(exec_obj)
    return exec_obj


# ── 继续 ──

def resume_execution(db: Session, exec_obj: PipelineExecution) -> PipelineExecution:
    if exec_obj.status != "paused":
        return exec_obj
    exec_obj.status = "running"
    db.commit()
    db.refresh(exec_obj)
    return exec_obj


# ── 删除 ──

def delete_execution(db: Session, exec_obj: PipelineExecution):
    db.delete(exec_obj)
    db.commit()


# ── 模拟执行 ──

def simulate_execution(db: Session, exec_obj: PipelineExecution) -> PipelineExecution:
    """
    模拟推进流水线执行：
    - 将所有 waiting stage 依次标记为 completed，填入模拟数据
    - 最终将 execution 标记为 completed
    """
    now = datetime.utcnow()
    exec_obj.status = "running"
    if not exec_obj.started_at:
        exec_obj.started_at = now
    db.flush()

    base_time = exec_obj.started_at or now

    for stage in sorted(exec_obj.stages, key=lambda s: s.stage_no):
        if stage.status == "completed":
            continue

        stage.status = "running"
        stage.model = SIMULATE_MODELS.get(stage.stage_no, "GPT-4o")
        stage.started_at = base_time + timedelta(seconds=random.randint(1, 5))

        # 模拟耗时
        duration = random.randint(30, 300)  # 30s ~ 5min
        stage.duration_ms = duration * 1000
        stage.completed_at = stage.started_at + timedelta(seconds=duration)

        # 模拟 token
        stage.input_tokens = random.randint(5000, 25000)
        stage.output_tokens = random.randint(2000, 15000)

        # 模拟 result_summary
        summary = SIMULATE_SUMMARIES.get(stage.stage_no, {})
        # 每次生成新的随机值
        if stage.stage_no == 1:
            summary = {k: random.randint(v - 5, v + 10) for k, v in summary.items()}
        elif stage.stage_no == 2:
            summary = {k: random.randint(max(1, v - 10), v + 15) for k, v in summary.items()}
        elif stage.stage_no == 3:
            summary = {k: (f"{random.randint(60, 98)}%" if k == "覆盖率" else random.randint(max(1, v - 5), v + 10)) for k, v in summary.items()}
        elif stage.stage_no == 4:
            summary = {k: random.randint(max(0, v - 3), v + 5) for k, v in summary.items()}
        stage.result_summary = summary

        stage.status = "completed"
        base_time = stage.completed_at

        db.flush()

    exec_obj.status = "completed"
    exec_obj.completed_at = base_time
    if exec_obj.started_at and exec_obj.completed_at:
        delta = exec_obj.completed_at - exec_obj.started_at
        exec_obj.total_duration_ms = int(delta.total_seconds() * 1000)

    db.commit()
    db.refresh(exec_obj)
    return exec_obj
