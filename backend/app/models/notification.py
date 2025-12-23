"""
通知模型
作者：张彦龙
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    """通知类型"""
    APPROVAL_PENDING = "审批待办"  # 审批待办提醒
    THRESHOLD_WARNING = "阈值预警"  # 阈值预警通知
    ANOMALY_ALERT = "异常告警"  # 异常行为告警
    SYSTEM_NOTICE = "系统通知"  # 系统通知
    REMINDER = "提醒"  # 一般提醒


class NotificationStatus(str, enum.Enum):
    """通知状态"""
    UNREAD = "未读"
    READ = "已读"
    ARCHIVED = "已归档"


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="接收用户ID")
    type = Column(SQLEnum(NotificationType), nullable=False, comment="通知类型")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, comment="通知内容")
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.UNREAD, comment="通知状态")
    
    # 关联资源信息（可选）
    resource_type = Column(String(50), comment="关联资源类型（如：scenario, approval等）")
    resource_id = Column(Integer, comment="关联资源ID")
    
    # 元数据
    action_url = Column(String(500), comment="操作链接（点击通知后跳转的URL）")
    priority = Column(Integer, default=0, comment="优先级（0-普通，1-重要，2-紧急）")
    is_read = Column(Boolean, default=False, index=True, comment="是否已读")
    read_at = Column(DateTime(timezone=True), comment="阅读时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", backref="notifications")

