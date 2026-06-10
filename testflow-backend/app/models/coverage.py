from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class FeaturePointTestCase(Base):
    __tablename__ = "feature_point_testcases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_point_id = Column(Integer, ForeignKey("feature_points.id", ondelete="CASCADE"), nullable=False)
    testcase_id = Column(Integer, ForeignKey("testcases.id", ondelete="CASCADE"), nullable=False)
    coverage_type = Column(String(30), default="functional")
    confidence = Column(Integer, default=100)
    evidence = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())

    feature_point = relationship("FeaturePoint", backref="testcase_coverages", passive_deletes=True)
    testcase = relationship("TestCase", backref="feature_coverages", passive_deletes=True)
