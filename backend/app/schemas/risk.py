"""
风险评估Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.models.risk import RiskLevel, AssessmentStatus


class RiskAssessmentBase(BaseModel):
    """风险评估基础模型"""
    assessment_name: str = Field(..., description="评估名称")
    assessment_code: str = Field(..., description="评估编码")
    assessment_type: str = Field("PIA", description="评估类型")
    scenario_id: int = Field(..., description="关联场景ID")


class RiskAssessmentCreate(RiskAssessmentBase):
    """创建风险评估"""
    assessor_id: Optional[int] = Field(None, description="评估人ID")


class RiskAssessmentUpdate(BaseModel):
    """更新风险评估"""
    legal_environment_score: Optional[Decimal] = None
    data_volume_score: Optional[Decimal] = None
    security_measures_score: Optional[Decimal] = None
    data_sensitivity_score: Optional[Decimal] = None
    personal_info_count: Optional[Decimal] = None
    sensitive_info_count: Optional[Decimal] = None
    mitigation_measures: Optional[str] = None
    assessment_result: Optional[str] = None
    recommendation: Optional[str] = None


class RiskAssessmentResponse(RiskAssessmentBase):
    """风险评估响应模型"""
    id: int
    legal_environment_score: Optional[Decimal]
    data_volume_score: Optional[Decimal]
    security_measures_score: Optional[Decimal]
    data_sensitivity_score: Optional[Decimal]
    personal_info_count: Optional[Decimal]
    sensitive_info_count: Optional[Decimal]
    exceeds_personal_threshold: bool
    exceeds_sensitive_threshold: bool
    overall_risk_level: Optional[RiskLevel]
    overall_score: Optional[Decimal]
    risk_factors: Optional[Dict[str, Any]]
    mitigation_measures: Optional[str]
    assessment_result: Optional[str]
    requires_regulatory_approval: bool
    recommendation: Optional[str]
    status: AssessmentStatus
    assessor_id: Optional[int]
    reviewed_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

