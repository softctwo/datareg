"""
传输审批Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.scenario import ApprovalStatus


class TransferApprovalBase(BaseModel):
    """传输审批基础模型"""
    scenario_id: int = Field(..., description="场景ID")
    transfer_type: Optional[str] = Field(None, description="传输类型")
    data_assets: Optional[List[int]] = Field(None, description="涉及的数据资产ID列表")


class TransferApprovalCreate(TransferApprovalBase):
    """创建传输审批"""
    applicant_id: int = Field(..., description="申请人ID")


class TransferApprovalUpdate(BaseModel):
    """更新传输审批"""
    transfer_start_time: Optional[datetime] = None
    transfer_end_time: Optional[datetime] = None
    actual_volume: Optional[Decimal] = None


class TransferApprovalResponse(TransferApprovalBase):
    """传输审批响应模型"""
    id: int
    approval_status: ApprovalStatus
    applicant_id: int
    approver_id: Optional[int]
    transfer_start_time: Optional[datetime]
    transfer_end_time: Optional[datetime]
    actual_volume: Optional[Decimal]
    approval_comment: Optional[str]
    approved_at: Optional[datetime]
    rejected_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

