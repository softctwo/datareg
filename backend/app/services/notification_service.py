"""
通知服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict
from datetime import datetime
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationStats
from app.utils.config_helper import ConfigHelper


class NotificationService:
    """通知服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_helper = ConfigHelper(db)
    
    def create_notification(self, notification_data: NotificationCreate) -> Optional[Notification]:
        """创建通知"""
        # 检查站内通知是否启用
        if not self.config_helper.get_in_app_notification_enabled():
            # 站内通知未启用，不创建通知
            return None
        
        db_notification = Notification(**notification_data.model_dump())
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification
    
    def get_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None
    ) -> List[Notification]:
        """获取用户通知列表"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if is_read is not None:
            # 同时检查is_read和status字段
            if is_read:
                query = query.filter(
                    (Notification.is_read == True) | (Notification.status == NotificationStatus.READ)
                )
            else:
                query = query.filter(
                    (Notification.is_read == False) & (Notification.status == NotificationStatus.UNREAD)
                )
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_notification(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """获取通知详情"""
        return self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """标记通知为已读"""
        notification = self.get_notification(notification_id, user_id)
        if not notification:
            return None
        
        notification.is_read = True
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now()
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def mark_all_as_read(self, user_id: int) -> int:
        """标记所有通知为已读"""
        count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({
            Notification.is_read: True,
            Notification.status: NotificationStatus.READ,
            Notification.read_at: datetime.now()
        })
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """删除通知"""
        notification = self.get_notification(notification_id, user_id)
        if not notification:
            return False
        
        self.db.delete(notification)
        self.db.commit()
        return True
    
    def get_stats(self, user_id: int) -> NotificationStats:
        """获取通知统计"""
        total = self.db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id
        ).scalar()
        
        unread = self.db.query(func.count(Notification.id)).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).scalar()
        
        read = total - unread if total else 0
        
        # 按类型统计
        by_type = {}
        type_counts = self.db.query(
            Notification.type,
            func.count(Notification.id)
        ).filter(
            Notification.user_id == user_id
        ).group_by(Notification.type).all()
        
        for notif_type, count in type_counts:
            by_type[notif_type.value] = count
        
        return NotificationStats(
            total=total or 0,
            unread=unread or 0,
            read=read or 0,
            by_type=by_type
        )
    
    def create_approval_notification(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        title: str,
        content: str,
        action_url: Optional[str] = None
    ) -> Notification:
        """创建审批待办通知"""
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.APPROVAL_PENDING,
            title=title,
            content=content,
            resource_type=resource_type,
            resource_id=resource_id,
            action_url=action_url,
            priority=1
        )
        return self.create_notification(notification_data)
    
    def create_threshold_warning(
        self,
        user_id: int,
        title: str,
        content: str,
        action_url: Optional[str] = None
    ) -> Notification:
        """创建阈值预警通知"""
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.THRESHOLD_WARNING,
            title=title,
            content=content,
            action_url=action_url,
            priority=2
        )
        return self.create_notification(notification_data)
    
    def create_anomaly_alert(
        self,
        user_id: int,
        title: str,
        content: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        action_url: Optional[str] = None
    ) -> Notification:
        """创建异常告警通知"""
        notification_data = NotificationCreate(
            user_id=user_id,
            type=NotificationType.ANOMALY_ALERT,
            title=title,
            content=content,
            resource_type=resource_type,
            resource_id=resource_id,
            action_url=action_url,
            priority=2
        )
        return self.create_notification(notification_data)

