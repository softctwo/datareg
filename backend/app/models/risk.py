"""
风险评估模型
作者：张彦龙
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class RiskLevel(str, enum.Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    CRITICAL = "极高风险"


class AssessmentStatus(str, enum.Enum):
    """评估状态"""
    DRAFT = "草稿"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    ARCHIVED = "已归档"


class RiskAssessment(Base):
    """风险评估表（PIA/DPIA）"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_name = Column(String(200), nullable=False, index=True, comment="评估名称")
    assessment_code = Column(String(100), unique=True, nullable=False, index=True, comment="评估编码")
    assessment_type = Column(String(50), default="PIA", comment="评估类型：PIA/DPIA")
    
    # 关联场景
    scenario_id = Column(Integer, ForeignKey("cross_border_scenarios.id"), nullable=False, index=True)
    
    # 评估维度
    legal_environment_score = Column(Numeric(5, 2), comment="境外接收方所在国法律环境评分（0-100）")
    data_volume_score = Column(Numeric(5, 2), comment="数据规模评分（0-100）")
    security_measures_score = Column(Numeric(5, 2), comment="安全措施评分（0-100）")
    data_sensitivity_score = Column(Numeric(5, 2), comment="数据敏感性评分（0-100）")
    
    # 阈值检查
    personal_info_count = Column(Numeric(20, 0), default=0, comment="个人信息数量")
    sensitive_info_count = Column(Numeric(20, 0), default=0, comment="敏感个人信息数量")
    exceeds_personal_threshold = Column(Boolean, default=False, comment="是否超过个人信息阈值")
    exceeds_sensitive_threshold = Column(Boolean, default=False, comment="是否超过敏感信息阈值")
    
    # 综合评估
    overall_risk_level = Column(SQLEnum(RiskLevel), comment="综合风险等级")
    overall_score = Column(Numeric(5, 2), comment="综合评分（0-100）")
    risk_factors = Column(JSON, comment="风险因素（JSON）")
    mitigation_measures = Column(Text, comment="缓解措施")
    
    # 评估结果
    assessment_result = Column(Text, comment="评估结论")
    requires_regulatory_approval = Column(Boolean, default=False, comment="是否需要监管审批")
    recommendation = Column(Text, comment="建议")
    
    # 状态
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, comment="评估状态")
    assessor_id = Column(Integer, ForeignKey("users.id"), comment="评估人ID")
    reviewed_by = Column(Integer, ForeignKey("users.id"), comment="审核人ID")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    
    # 关系
    scenario = relationship("CrossBorderScenario")
    assessor = relationship("User", foreign_keys=[assessor_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

