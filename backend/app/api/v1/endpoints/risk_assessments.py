"""
风险评估API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.risk import (
    RiskAssessmentCreate, RiskAssessmentUpdate,
    RiskAssessmentResponse
)
from app.services.risk_service import RiskAssessmentService

router = APIRouter()


@router.get("/", response_model=List[RiskAssessmentResponse])
async def list_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scenario_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取风险评估列表"""
    service = RiskAssessmentService(db)
    assessments = service.list_assessments(skip=skip, limit=limit, scenario_id=scenario_id, status=status)
    # 确保Enum正确序列化
    result = []
    for assessment in assessments:
        result.append(RiskAssessmentResponse.model_validate(assessment))
    return result


@router.get("/{assessment_id}", response_model=RiskAssessmentResponse)
async def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """获取风险评估详情"""
    service = RiskAssessmentService(db)
    assessment = service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="风险评估不存在")
    return RiskAssessmentResponse.model_validate(assessment)


@router.post("/", response_model=RiskAssessmentResponse)
async def create_assessment(
    assessment: RiskAssessmentCreate,
    db: Session = Depends(get_db)
):
    """创建风险评估"""
    service = RiskAssessmentService(db)
    created = service.create_assessment(assessment)
    return RiskAssessmentResponse.model_validate(created)


@router.post("/{assessment_id}/calculate", response_model=RiskAssessmentResponse)
async def calculate_risk(assessment_id: int, db: Session = Depends(get_db)):
    """执行风险评估计算"""
    service = RiskAssessmentService(db)
    assessment = service.calculate_risk(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="风险评估不存在")
    return RiskAssessmentResponse.model_validate(assessment)


@router.get("/{assessment_id}/threshold-check", response_model=dict)
async def check_thresholds(assessment_id: int, db: Session = Depends(get_db)):
    """检查阈值预警"""
    service = RiskAssessmentService(db)
    result = service.check_thresholds(assessment_id)
    if not result:
        raise HTTPException(status_code=404, detail="风险评估不存在")
    return result

