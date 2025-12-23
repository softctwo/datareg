"""
通知API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse, NotificationStats
)
from app.models.notification import NotificationType
from app.services.notification_service import NotificationService
from app.core.permissions import get_current_user_id, require_permission

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_read: Optional[bool] = None,
    notification_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取当前用户的通知列表"""
    service = NotificationService(db)
    notif_type = None
    if notification_type:
        try:
            notif_type = NotificationType(notification_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的通知类型: {notification_type}")
    
    return service.get_notifications(
        user_id=user_id,
        skip=skip,
        limit=limit,
        is_read=is_read,
        notification_type=notif_type
    )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取通知统计"""
    service = NotificationService(db)
    return service.get_stats(user_id)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """获取通知详情"""
    service = NotificationService(db)
    notification = service.get_notification(notification_id, user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    return notification


@router.post("/", response_model=NotificationResponse, dependencies=[Depends(require_permission("notification:write"))])
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """创建通知（管理员功能）"""
    service = NotificationService(db)
    return service.create_notification(notification)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """标记通知为已读"""
    service = NotificationService(db)
    notification = service.mark_as_read(notification_id, user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    return notification


@router.put("/read-all", response_model=dict)
async def mark_all_as_read(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """标记所有通知为已读"""
    service = NotificationService(db)
    count = service.mark_all_as_read(user_id)
    return {"message": f"已标记 {count} 条通知为已读", "count": count}


@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """删除通知"""
    service = NotificationService(db)
    success = service.delete_notification(notification_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")
    return {"message": "通知已删除"}

