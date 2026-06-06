from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TestCase(Base):
    __tablename__ = "testcases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_no = Column(String(60), nullable=False)  # SPD_TC_DL_001
    title = Column(String(200), nullable=False)
    priority = Column(String(10), nullable=False, default="中")  # 高/中/低
    exec_status = Column(String(20), nullable=False, default="待执行")  # 通过/失败/执行中/待执行
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    module = Column(String(50), nullable=True)  # 模块代码缓存，如 DL、SJZH
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True)  # FK → modules 表
    preconditions = Column(Text, default="")  # 前置条件
    test_data = Column(Text, default="")  # 测试数据
    test_steps = Column(Text, default="")  # 测试步骤
    expected_result = Column(Text, default="")  # 预期结果
    actual_result = Column(Text, default="")  # 实际结果
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    executor = relationship("User", backref="executed_cases")
    project = relationship("Project", backref="testcases")
