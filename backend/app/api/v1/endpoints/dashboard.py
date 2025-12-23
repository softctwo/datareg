"""
监控仪表盘API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/overview", response_model=dict)
async def get_overview(
    days: int = Query(7, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db)
):
    """获取概览统计"""
    service = DashboardService(db)
    return service.get_overview(days=days)


@router.get("/transfer-trends", response_model=dict)
async def get_transfer_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取传输趋势"""
    service = DashboardService(db)
    return service.get_transfer_trends(days=days)


@router.get("/country-distribution", response_model=dict)
async def get_country_distribution(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取目的国分布"""
    service = DashboardService(db)
    return service.get_country_distribution(days=days)


@router.get("/risk-alerts", response_model=dict)
async def get_risk_alerts(db: Session = Depends(get_db)):
    """获取风险预警"""
    service = DashboardService(db)
    return service.get_risk_alerts()


@router.get("/data-asset-statistics", response_model=dict)
async def get_data_asset_statistics(db: Session = Depends(get_db)):
    """获取数据资产统计"""
    service = DashboardService(db)
    return service.get_data_asset_statistics()


@router.get("/risk-statistics", response_model=dict)
async def get_risk_statistics(db: Session = Depends(get_db)):
    """获取风险评估统计"""
    service = DashboardService(db)
    return service.get_risk_statistics()


@router.get("/approval-statistics", response_model=dict)
async def get_approval_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取审批统计"""
    service = DashboardService(db)
    return service.get_approval_statistics(days=days)


@router.get("/operation-statistics", response_model=dict)
async def get_operation_statistics(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取操作统计"""
    service = DashboardService(db)
    return service.get_operation_statistics(days=days)


@router.get("/heatmap", response_model=dict)
async def get_heatmap_data(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取热力图数据（操作类型 x 日期）"""
    service = DashboardService(db)
    return service.get_heatmap_data(days=days)


@router.get("/approval-funnel", response_model=dict)
async def get_approval_funnel(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取审批流程漏斗数据"""
    service = DashboardService(db)
    return service.get_approval_funnel(days=days)


@router.get("/risk-scatter", response_model=dict)
async def get_risk_scatter(db: Session = Depends(get_db)):
    """获取风险评估散点图数据"""
    service = DashboardService(db)
    return service.get_risk_scatter()


@router.get("/risk-radar", response_model=dict)
async def get_risk_radar(
    assessment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取风险评估雷达图数据"""
    service = DashboardService(db)
    return service.get_risk_radar(assessment_id=assessment_id)

