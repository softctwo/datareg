"""
传输审批API端点
作者：张彦龙
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.approval import (
    TransferApprovalCreate, TransferApprovalUpdate,
    TransferApprovalResponse
)
from app.services.approval_service import ApprovalService

router = APIRouter()


@router.get("/", response_model=List[TransferApprovalResponse])
async def list_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scenario_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取传输审批列表"""
    service = ApprovalService(db)
    approvals = service.list_approvals(skip=skip, limit=limit, scenario_id=scenario_id, status=status)
    # 转换data_assets从JSON字符串到列表
    result = []
    for approval in approvals:
        # 先手动构建字典，转换data_assets
        approval_dict = {
            "id": approval.id,
            "scenario_id": approval.scenario_id,
            "approval_status": approval.approval_status,
            "applicant_id": approval.applicant_id,
            "approver_id": approval.approver_id,
            "transfer_type": approval.transfer_type,
            "transfer_start_time": approval.transfer_start_time,
            "transfer_end_time": approval.transfer_end_time,
            "actual_volume": approval.actual_volume,
            "approval_comment": approval.approval_comment,
            "approved_at": approval.approved_at,
            "rejected_reason": approval.rejected_reason,
            "created_at": approval.created_at,
            "updated_at": approval.updated_at,
        }
        # 处理data_assets字段
        if approval.data_assets:
            try:
                approval_dict["data_assets"] = json.loads(approval.data_assets)
            except (json.JSONDecodeError, TypeError):
                approval_dict["data_assets"] = []
        else:
            approval_dict["data_assets"] = []
        result.append(TransferApprovalResponse(**approval_dict))
    return result


@router.get("/{approval_id}", response_model=TransferApprovalResponse)
async def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """获取审批详情"""
    service = ApprovalService(db)
    approval = service.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="审批记录不存在")
    # 手动构建字典，转换data_assets
    approval_dict = {
        "id": approval.id,
        "scenario_id": approval.scenario_id,
        "approval_status": approval.approval_status,
        "applicant_id": approval.applicant_id,
        "approver_id": approval.approver_id,
        "transfer_type": approval.transfer_type,
        "transfer_start_time": approval.transfer_start_time,
        "transfer_end_time": approval.transfer_end_time,
        "actual_volume": approval.actual_volume,
        "approval_comment": approval.approval_comment,
        "approved_at": approval.approved_at,
        "rejected_reason": approval.rejected_reason,
        "created_at": approval.created_at,
        "updated_at": approval.updated_at,
    }
    # 处理data_assets字段
    if approval.data_assets:
        try:
            approval_dict["data_assets"] = json.loads(approval.data_assets)
        except (json.JSONDecodeError, TypeError):
            approval_dict["data_assets"] = []
    else:
        approval_dict["data_assets"] = []
    return TransferApprovalResponse(**approval_dict)


@router.post("/", response_model=TransferApprovalResponse)
async def create_approval(
    approval: TransferApprovalCreate,
    db: Session = Depends(get_db)
):
    """创建传输审批申请"""
    service = ApprovalService(db)
    created = service.create_approval(approval)
    # 手动构建字典，转换data_assets
    approval_dict = {
        "id": created.id,
        "scenario_id": created.scenario_id,
        "approval_status": created.approval_status,
        "applicant_id": created.applicant_id,
        "approver_id": created.approver_id,
        "transfer_type": created.transfer_type,
        "transfer_start_time": created.transfer_start_time,
        "transfer_end_time": created.transfer_end_time,
        "actual_volume": created.actual_volume,
        "approval_comment": created.approval_comment,
        "approved_at": created.approved_at,
        "rejected_reason": created.rejected_reason,
        "created_at": created.created_at,
        "updated_at": created.updated_at,
    }
    # 处理data_assets字段
    if created.data_assets:
        try:
            approval_dict["data_assets"] = json.loads(created.data_assets)
        except (json.JSONDecodeError, TypeError):
            approval_dict["data_assets"] = []
    else:
        approval_dict["data_assets"] = []
    return TransferApprovalResponse(**approval_dict)


@router.post("/{approval_id}/approve", response_model=TransferApprovalResponse)
async def approve_transfer(
    approval_id: int,
    approver_id: int,
    comment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """批准传输"""
    service = ApprovalService(db)
    approval = service.approve_transfer(approval_id, approver_id, comment)
    if not approval:
        raise HTTPException(status_code=404, detail="审批记录不存在")
    # 手动构建字典，转换data_assets
    approval_dict = {
        "id": approval.id,
        "scenario_id": approval.scenario_id,
        "approval_status": approval.approval_status,
        "applicant_id": approval.applicant_id,
        "approver_id": approval.approver_id,
        "transfer_type": approval.transfer_type,
        "transfer_start_time": approval.transfer_start_time,
        "transfer_end_time": approval.transfer_end_time,
        "actual_volume": approval.actual_volume,
        "approval_comment": approval.approval_comment,
        "approved_at": approval.approved_at,
        "rejected_reason": approval.rejected_reason,
        "created_at": approval.created_at,
        "updated_at": approval.updated_at,
    }
    # 处理data_assets字段
    if approval.data_assets:
        try:
            approval_dict["data_assets"] = json.loads(approval.data_assets)
        except (json.JSONDecodeError, TypeError):
            approval_dict["data_assets"] = []
    else:
        approval_dict["data_assets"] = []
    return TransferApprovalResponse(**approval_dict)


@router.post("/{approval_id}/reject", response_model=TransferApprovalResponse)
async def reject_transfer(
    approval_id: int,
    approver_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """拒绝传输"""
    service = ApprovalService(db)
    approval = service.reject_transfer(approval_id, approver_id, reason)
    if not approval:
        raise HTTPException(status_code=404, detail="审批记录不存在")
    # 手动构建字典，转换data_assets
    approval_dict = {
        "id": approval.id,
        "scenario_id": approval.scenario_id,
        "approval_status": approval.approval_status,
        "applicant_id": approval.applicant_id,
        "approver_id": approval.approver_id,
        "transfer_type": approval.transfer_type,
        "transfer_start_time": approval.transfer_start_time,
        "transfer_end_time": approval.transfer_end_time,
        "actual_volume": approval.actual_volume,
        "approval_comment": approval.approval_comment,
        "approved_at": approval.approved_at,
        "rejected_reason": approval.rejected_reason,
        "created_at": approval.created_at,
        "updated_at": approval.updated_at,
    }
    # 处理data_assets字段
    if approval.data_assets:
        try:
            approval_dict["data_assets"] = json.loads(approval.data_assets)
        except (json.JSONDecodeError, TypeError):
            approval_dict["data_assets"] = []
    else:
        approval_dict["data_assets"] = []
    return TransferApprovalResponse(**approval_dict)

