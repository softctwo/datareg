"""
审计日志API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    is_anomaly: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取审计日志列表"""
    service = AuditService(db)
    return service.list_logs(
        skip=skip, limit=limit, action=action,
        resource_type=resource_type, user_id=user_id,
        start_date=start_date, end_date=end_date,
        is_anomaly=is_anomaly
    )


@router.get("/statistics", response_model=dict)
async def get_audit_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """获取审计统计信息"""
    service = AuditService(db)
    return service.get_statistics(start_date=start_date, end_date=end_date)


@router.get("/anomalies", response_model=List[AuditLogResponse])
async def list_anomalies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取异常行为列表"""
    service = AuditService(db)
    return service.list_anomalies(skip=skip, limit=limit)

