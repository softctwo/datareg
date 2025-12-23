"""
审计日志模型
作者：张彦龙
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AuditAction(str, enum.Enum):
    """审计操作类型"""
    CREATE = "创建"
    UPDATE = "更新"
    DELETE = "删除"
    APPROVE = "审批"
    REJECT = "拒绝"
    TRANSFER = "传输"
    INTERCEPT = "拦截"
    DESENSITIZE = "脱敏"
    VIEW = "查看"
    EXPORT = "导出"


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 操作信息
    action = Column(SQLEnum(AuditAction), nullable=False, index=True, comment="操作类型")
    resource_type = Column(String(50), index=True, comment="资源类型：数据资产/场景/审批/评估")
    resource_id = Column(Integer, index=True, comment="资源ID")
    
    # 用户信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    username = Column(String(50), comment="用户名（冗余字段，便于查询）")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="用户代理")
    
    # 操作详情
    operation_details = Column(JSON, comment="操作详情（JSON）")
    before_data = Column(JSON, comment="操作前数据（JSON）")
    after_data = Column(JSON, comment="操作后数据（JSON）")
    
    # 传输相关
    transfer_volume = Column(Numeric(20, 0), comment="传输数据量")
    destination_country = Column(String(100), comment="目的国")
    transfer_status = Column(String(50), comment="传输状态：成功/失败/拦截")
    
    # 异常标记
    is_anomaly = Column(Boolean, default=False, index=True, comment="是否异常")
    anomaly_type = Column(String(50), comment="异常类型")
    anomaly_reason = Column(Text, comment="异常原因")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 关系
    user = relationship("User")

