"""
通知Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType, NotificationStatus


class NotificationBase(BaseModel):
    """通知基础模型"""
    type: NotificationType
    title: str = Field(..., description="通知标题")
    content: Optional[str] = Field(None, description="通知内容")
    resource_type: Optional[str] = Field(None, description="关联资源类型")
    resource_id: Optional[int] = Field(None, description="关联资源ID")
    action_url: Optional[str] = Field(None, description="操作链接")
    priority: int = Field(0, ge=0, le=2, description="优先级（0-普通，1-重要，2-紧急）")


class NotificationCreate(NotificationBase):
    """创建通知"""
    user_id: int = Field(..., description="接收用户ID")


class NotificationUpdate(BaseModel):
    """更新通知"""
    status: Optional[NotificationStatus] = None
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """通知响应模型"""
    id: int
    user_id: int
    status: NotificationStatus
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """通知统计"""
    total: int
    unread: int
    read: int
    by_type: dict = Field(default_factory=dict, description="按类型统计")

