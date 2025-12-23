"""
跨境传输场景API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.scenario import (
    CrossBorderScenarioCreate, CrossBorderScenarioUpdate,
    CrossBorderScenarioResponse
)
from app.services.scenario_service import ScenarioService

router = APIRouter()


@router.get("/", response_model=List[CrossBorderScenarioResponse])
async def list_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    recipient_country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取跨境传输场景列表"""
    service = ScenarioService(db)
    return service.list_scenarios(skip=skip, limit=limit, status=status, recipient_country=recipient_country)


@router.get("/{scenario_id}", response_model=CrossBorderScenarioResponse)
async def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """获取场景详情"""
    service = ScenarioService(db)
    scenario = service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")
    return scenario


@router.post("/", response_model=CrossBorderScenarioResponse)
async def create_scenario(
    scenario: CrossBorderScenarioCreate,
    db: Session = Depends(get_db)
):
    """创建跨境传输场景"""
    service = ScenarioService(db)
    return service.create_scenario(scenario)


@router.put("/{scenario_id}", response_model=CrossBorderScenarioResponse)
async def update_scenario(
    scenario_id: int,
    scenario: CrossBorderScenarioUpdate,
    db: Session = Depends(get_db)
):
    """更新场景"""
    service = ScenarioService(db)
    updated = service.update_scenario(scenario_id, scenario)
    if not updated:
        raise HTTPException(status_code=404, detail="场景不存在")
    return updated


@router.post("/{scenario_id}/submit", response_model=CrossBorderScenarioResponse)
async def submit_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """提交场景审批"""
    service = ScenarioService(db)
    scenario = service.submit_for_approval(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")
    return scenario


@router.post("/{scenario_id}/approve", response_model=CrossBorderScenarioResponse)
async def approve_scenario(
    scenario_id: int,
    approver_id: int,
    comment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """批准场景"""
    service = ScenarioService(db)
    scenario = service.approve_scenario(scenario_id, approver_id, comment)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")
    return scenario


@router.post("/{scenario_id}/reject", response_model=CrossBorderScenarioResponse)
async def reject_scenario(
    scenario_id: int,
    approver_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """拒绝场景"""
    service = ScenarioService(db)
    scenario = service.reject_scenario(scenario_id, approver_id, reason)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")
    return scenario

