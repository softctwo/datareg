"""
拦截与脱敏API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.interception import (
    WhitelistEntry, BlacklistEntry, InterceptionCheckRequest,
    InterceptionCheckResponse, DesensitizationRequest, DesensitizationResponse
)
from app.services.interception_service import InterceptionService
from app.services.approval_service import ApprovalService
from app.services.data_asset_service import DataAssetService
from app.core.permissions import require_permission

router = APIRouter()


@router.post("/check", response_model=InterceptionCheckResponse)
async def check_interception(
    request: InterceptionCheckRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:read"))
):
    """检查是否需要拦截"""
    service = InterceptionService(db)
    result = service.check_interception(
        approval_id=request.approval_id,
        asset_ids=request.asset_ids,
        data=request.data or {}
    )
    return InterceptionCheckResponse(**result)


@router.get("/whitelist", response_model=List[WhitelistEntry])
async def get_whitelist(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:read"))
):
    """获取白名单列表"""
    service = InterceptionService(db)
    approval_service = ApprovalService(db)
    
    # 从已批准的审批中获取白名单
    approvals = approval_service.list_approvals(
        skip=0,
        limit=1000,
        status="APPROVED"
    )
    
    whitelist_entries = []
    for approval in approvals:
        # 所有已批准的审批都应该显示在白名单中
        # 获取场景信息
        scenario = None
        if approval.scenario_id:
            from app.services.scenario_service import ScenarioService
            scenario_service = ScenarioService(db)
            scenario = scenario_service.get_scenario(approval.scenario_id)
        
        # 获取资产信息
        asset_ids = []
        if approval.data_assets:
            if isinstance(approval.data_assets, list):
                asset_ids = approval.data_assets
            elif isinstance(approval.data_assets, str):
                import json
                try:
                    asset_ids = json.loads(approval.data_assets)
                except:
                    asset_ids = []
        
        # 使用approved_at或created_at作为添加时间
        added_at = approval.approved_at if hasattr(approval, 'approved_at') and approval.approved_at else approval.created_at
        
        whitelist_entries.append(WhitelistEntry(
            approval_id=approval.id,
            scenario_id=scenario.id if scenario else None,
            scenario_name=scenario.scenario_name if scenario else None,
            asset_ids=asset_ids,
            added_at=added_at
        ))
    
    return whitelist_entries


@router.post("/whitelist/{approval_id}", response_model=dict)
async def add_to_whitelist(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:write"))
):
    """添加到白名单"""
    service = InterceptionService(db)
    approval_service = ApprovalService(db)
    
    approval = approval_service.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")
    
    service.add_to_whitelist(approval)
    return {"message": "已添加到白名单", "approval_id": approval_id}


@router.delete("/whitelist/{approval_id}", response_model=dict)
async def remove_from_whitelist(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:write"))
):
    """从白名单移除"""
    service = InterceptionService(db)
    service.remove_from_whitelist(approval_id)
    return {"message": "已从白名单移除", "approval_id": approval_id}


@router.get("/blacklist", response_model=List[BlacklistEntry])
async def get_blacklist(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:read"))
):
    """获取黑名单列表"""
    service = InterceptionService(db)
    asset_service = DataAssetService(db)
    
    blacklist_entries = []
    for asset_id in service.blacklist:
        asset = asset_service.get_asset(asset_id)
        if asset:
            from datetime import datetime
            blacklist_entries.append(BlacklistEntry(
                asset_id=asset.id,
                asset_name=asset.asset_name,
                asset_code=asset.asset_code,
                data_level=asset.data_level.value if asset.data_level else None,
                reason="手动添加到黑名单",
                added_at=datetime.now()  # 使用当前时间作为添加时间
            ))
    
    return blacklist_entries


@router.post("/blacklist/{asset_id}", response_model=dict)
async def add_to_blacklist(
    asset_id: int,
    reason: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:write"))
):
    """添加到黑名单"""
    service = InterceptionService(db)
    asset_service = DataAssetService(db)
    
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="数据资产不存在")
    
    service.add_to_blacklist(asset_id)
    return {"message": "已添加到黑名单", "asset_id": asset_id, "reason": reason}


@router.delete("/blacklist/{asset_id}", response_model=dict)
async def remove_from_blacklist(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:write"))
):
    """从黑名单移除"""
    service = InterceptionService(db)
    service.remove_from_blacklist(asset_id)
    return {"message": "已从黑名单移除", "asset_id": asset_id}


@router.post("/desensitize", response_model=DesensitizationResponse)
async def desensitize_data(
    request: DesensitizationRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_permission("interception:read"))
):
    """对数据进行脱敏处理"""
    service = InterceptionService(db)
    desensitized_data = service.desensitizer.desensitize(
        request.data,
        request.asset_ids or []
    )
    
    # 找出被脱敏的字段
    desensitized_fields = []
    for key, value in request.data.items():
        if key in desensitized_data and value != desensitized_data[key]:
            desensitized_fields.append(key)
    
    return DesensitizationResponse(
        original_data=request.data,
        desensitized_data=desensitized_data,
        desensitized_fields=desensitized_fields
    )

