"""
审计服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.audit import AuditLog, AuditAction


class AuditService:
    """审计服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_anomaly: Optional[bool] = None
    ) -> List[AuditLog]:
        """获取审计日志列表"""
        query = self.db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if is_anomaly is not None:
            query = query.filter(AuditLog.is_anomaly == is_anomaly)
        
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取审计统计信息"""
        query = self.db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # 总操作数
        total_operations = query.count()
        
        # 按操作类型统计
        action_stats = (
            query.with_entities(AuditLog.action, func.count(AuditLog.id).label("count"))
            .group_by(AuditLog.action)
            .all()
        )
        
        # 异常操作数
        anomaly_count = query.filter(AuditLog.is_anomaly == True).count()
        
        # 传输相关统计
        transfer_logs = query.filter(AuditLog.action == AuditAction.TRANSFER).all()
        total_transfer_volume = sum(
            float(log.transfer_volume) for log in transfer_logs if log.transfer_volume
        )
        
        # 按目的国统计
        country_stats = (
            query.filter(AuditLog.destination_country.isnot(None))
            .with_entities(
                AuditLog.destination_country,
                func.count(AuditLog.id).label("count")
            )
            .group_by(AuditLog.destination_country)
            .all()
        )
        
        return {
            "total_operations": total_operations,
            "anomaly_count": anomaly_count,
            "action_statistics": {action: count for action, count in action_stats},
            "total_transfer_volume": total_transfer_volume,
            "country_statistics": {country: count for country, count in country_stats}
        }
    
    def list_anomalies(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """获取异常行为列表"""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.is_anomaly == True)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_log(
        self,
        action: AuditAction,
        user_id: int,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        operation_details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """创建审计日志"""
        db_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            operation_details=operation_details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log

