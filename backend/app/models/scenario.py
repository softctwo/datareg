"""
跨境传输场景模型
作者：张彦龙
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ScenarioStatus(str, enum.Enum):
    """场景状态"""
    DRAFT = "草稿"
    PENDING = "待审批"
    APPROVED = "已批准"
    REJECTED = "已拒绝"
    EXPIRED = "已过期"
    SUSPENDED = "已暂停"


class ApprovalStatus(str, enum.Enum):
    """审批状态"""
    PENDING = "待审批"
    APPROVED = "已批准"
    REJECTED = "已拒绝"
    CANCELLED = "已取消"


class CrossBorderScenario(Base):
    """跨境传输场景表"""
    __tablename__ = "cross_border_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(200), nullable=False, index=True, comment="场景名称")
    scenario_code = Column(String(100), unique=True, nullable=False, index=True, comment="场景编码")
    business_type = Column(String(100), comment="业务类型：审计/合规审查/报表汇总/其他")
    
    # 境外接收方信息
    recipient_name = Column(String(200), nullable=False, comment="接收方名称")
    recipient_country = Column(String(100), nullable=False, comment="接收方所在国")
    recipient_type = Column(String(50), comment="接收方类型：母行/境外分行/第三方机构")
    
    # 传输要素
    data_purpose = Column(Text, nullable=False, comment="数据用途")
    storage_duration = Column(Integer, comment="存储期限（天）")
    transfer_frequency = Column(String(50), comment="传输频率：实时/日/周/月/一次性")
    security_level = Column(String(50), comment="链路安全级别：高/中/低")
    encryption_method = Column(String(100), comment="加密方式")
    
    # 数据范围
    data_scope = Column(Text, comment="数据范围描述")
    estimated_volume = Column(Numeric(20, 0), comment="预估数据量")
    
    # 状态和审批
    status = Column(SQLEnum(ScenarioStatus), default=ScenarioStatus.DRAFT, comment="场景状态")
    approver_id = Column(Integer, ForeignKey("users.id"), comment="审批人ID")
    approved_at = Column(DateTime(timezone=True), comment="批准时间")
    expiry_date = Column(DateTime(timezone=True), comment="到期日期")
    
    # 元数据
    description = Column(Text, comment="描述")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approver_id])
    approvals = relationship("TransferApproval", back_populates="scenario")


class TransferApproval(Base):
    """传输审批表"""
    __tablename__ = "transfer_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("cross_border_scenarios.id"), nullable=False, index=True)
    
    # 审批信息
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, comment="审批状态")
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="申请人ID")
    approver_id = Column(Integer, ForeignKey("users.id"), comment="审批人ID")
    
    # 传输详情
    transfer_type = Column(String(50), comment="传输类型：API/文件/数据库")
    data_assets = Column(Text, comment="涉及的数据资产（JSON数组）")
    transfer_start_time = Column(DateTime(timezone=True), comment="传输开始时间")
    transfer_end_time = Column(DateTime(timezone=True), comment="传输结束时间")
    actual_volume = Column(Numeric(20, 0), comment="实际传输量")
    
    # 审批意见
    approval_comment = Column(Text, comment="审批意见")
    approved_at = Column(DateTime(timezone=True), comment="批准时间")
    rejected_reason = Column(Text, comment="拒绝原因")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    scenario = relationship("CrossBorderScenario", back_populates="approvals")
    applicant = relationship("User", foreign_keys=[applicant_id])
    approver_rel = relationship("User", foreign_keys=[approver_id])

