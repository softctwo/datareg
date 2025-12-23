"""
批量操作API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.scenario_service import ScenarioService
from app.services.approval_service import ApprovalService
from app.services.data_asset_service import DataAssetService

router = APIRouter()


@router.post("/scenarios/approve")
async def batch_approve_scenarios(
    scenario_ids: List[int] = Body(...),
    approver_id: int = Body(...),
    comment: str = Body(None),
    db: Session = Depends(get_db)
):
    """批量批准场景"""
    service = ScenarioService(db)
    results = []
    errors = []
    
    for scenario_id in scenario_ids:
        try:
            scenario = service.approve_scenario(scenario_id, approver_id, comment)
            if scenario:
                results.append(scenario_id)
            else:
                errors.append(f"场景 {scenario_id} 不存在或状态不允许")
        except Exception as e:
            errors.append(f"场景 {scenario_id}: {str(e)}")
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "success_ids": results,
        "errors": errors
    }


@router.post("/scenarios/reject")
async def batch_reject_scenarios(
    scenario_ids: List[int] = Body(...),
    approver_id: int = Body(...),
    reason: str = Body(...),
    db: Session = Depends(get_db)
):
    """批量拒绝场景"""
    service = ScenarioService(db)
    results = []
    errors = []
    
    for scenario_id in scenario_ids:
        try:
            scenario = service.reject_scenario(scenario_id, approver_id, reason)
            if scenario:
                results.append(scenario_id)
            else:
                errors.append(f"场景 {scenario_id} 不存在或状态不允许")
        except Exception as e:
            errors.append(f"场景 {scenario_id}: {str(e)}")
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "success_ids": results,
        "errors": errors
    }


@router.post("/approvals/approve")
async def batch_approve_transfers(
    approval_ids: List[int] = Body(...),
    approver_id: int = Body(...),
    comment: str = Body(None),
    db: Session = Depends(get_db)
):
    """批量批准传输"""
    service = ApprovalService(db)
    results = []
    errors = []
    
    for approval_id in approval_ids:
        try:
            approval = service.approve_transfer(approval_id, approver_id, comment)
            if approval:
                results.append(approval_id)
            else:
                errors.append(f"审批 {approval_id} 不存在或状态不允许")
        except Exception as e:
            errors.append(f"审批 {approval_id}: {str(e)}")
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "success_ids": results,
        "errors": errors
    }


@router.post("/approvals/reject")
async def batch_reject_transfers(
    approval_ids: List[int] = Body(...),
    approver_id: int = Body(...),
    reason: str = Body(...),
    db: Session = Depends(get_db)
):
    """批量拒绝传输"""
    service = ApprovalService(db)
    results = []
    errors = []
    
    for approval_id in approval_ids:
        try:
            approval = service.reject_transfer(approval_id, approver_id, reason)
            if approval:
                results.append(approval_id)
            else:
                errors.append(f"审批 {approval_id} 不存在或状态不允许")
        except Exception as e:
            errors.append(f"审批 {approval_id}: {str(e)}")
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "success_ids": results,
        "errors": errors
    }


@router.delete("/data-assets")
async def batch_delete_assets(
    asset_ids: List[int] = Body(...),
    db: Session = Depends(get_db)
):
    """批量删除数据资产"""
    service = DataAssetService(db)
    results = []
    errors = []
    
    for asset_id in asset_ids:
        try:
            asset = service.get_asset(asset_id)
            if asset:
                # 这里需要添加删除方法
                # service.delete_asset(asset_id)
                results.append(asset_id)
            else:
                errors.append(f"资产 {asset_id} 不存在")
        except Exception as e:
            errors.append(f"资产 {asset_id}: {str(e)}")
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "success_ids": results,
        "errors": errors
    }

