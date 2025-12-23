"""
审计日志Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    """审计日志响应模型"""
    id: int
    action: AuditAction
    resource_type: Optional[str]
    resource_id: Optional[int]
    user_id: int
    username: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    operation_details: Optional[Dict[str, Any]]
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    transfer_volume: Optional[Decimal]
    destination_country: Optional[str]
    transfer_status: Optional[str]
    is_anomaly: bool
    anomaly_type: Optional[str]
    anomaly_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

