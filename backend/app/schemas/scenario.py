"""
跨境传输场景Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.scenario import ScenarioStatus


class CrossBorderScenarioBase(BaseModel):
    """跨境场景基础模型"""
    scenario_name: str = Field(..., description="场景名称")
    scenario_code: str = Field(..., description="场景编码")
    business_type: Optional[str] = Field(None, description="业务类型")
    recipient_name: str = Field(..., description="接收方名称")
    recipient_country: str = Field(..., description="接收方所在国")
    recipient_type: Optional[str] = Field(None, description="接收方类型")
    data_purpose: str = Field(..., description="数据用途")
    storage_duration: Optional[int] = Field(None, description="存储期限（天）")
    transfer_frequency: Optional[str] = Field(None, description="传输频率")
    security_level: Optional[str] = Field(None, description="链路安全级别")
    encryption_method: Optional[str] = Field(None, description="加密方式")
    data_scope: Optional[str] = Field(None, description="数据范围描述")
    estimated_volume: Optional[Decimal] = Field(None, description="预估数据量")
    description: Optional[str] = Field(None, description="描述")


class CrossBorderScenarioCreate(CrossBorderScenarioBase):
    """创建跨境场景"""
    created_by: int = Field(..., description="创建人ID")


class CrossBorderScenarioUpdate(BaseModel):
    """更新跨境场景"""
    scenario_name: Optional[str] = None
    business_type: Optional[str] = None
    data_purpose: Optional[str] = None
    storage_duration: Optional[int] = None
    transfer_frequency: Optional[str] = None
    security_level: Optional[str] = None
    encryption_method: Optional[str] = None
    data_scope: Optional[str] = None
    estimated_volume: Optional[Decimal] = None
    description: Optional[str] = None


class CrossBorderScenarioResponse(CrossBorderScenarioBase):
    """跨境场景响应模型"""
    id: int
    status: ScenarioStatus
    approver_id: Optional[int]
    approved_at: Optional[datetime]
    expiry_date: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

