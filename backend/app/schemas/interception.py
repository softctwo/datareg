"""
拦截与脱敏Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class WhitelistEntry(BaseModel):
    """白名单条目"""
    approval_id: int = Field(..., description="审批ID")
    scenario_id: Optional[int] = Field(None, description="场景ID")
    scenario_name: Optional[str] = Field(None, description="场景名称")
    asset_ids: List[int] = Field(default_factory=list, description="数据资产ID列表")
    added_at: Optional[datetime] = Field(None, description="添加时间")


class BlacklistEntry(BaseModel):
    """黑名单条目"""
    asset_id: int = Field(..., description="数据资产ID")
    asset_name: Optional[str] = Field(None, description="资产名称")
    asset_code: Optional[str] = Field(None, description="资产代码")
    data_level: Optional[str] = Field(None, description="数据级别")
    reason: Optional[str] = Field(None, description="加入黑名单原因")
    added_at: Optional[datetime] = Field(None, description="添加时间")


class InterceptionCheckRequest(BaseModel):
    """拦截检查请求"""
    approval_id: Optional[int] = Field(None, description="审批ID")
    asset_ids: List[int] = Field(..., description="数据资产ID列表")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="待传输数据")


class InterceptionCheckResponse(BaseModel):
    """拦截检查响应"""
    allowed: bool = Field(..., description="是否允许传输")
    intercepted: bool = Field(..., description="是否被拦截")
    reason: Optional[str] = Field(None, description="拦截原因")
    desensitized_data: Optional[Dict[str, Any]] = Field(None, description="脱敏后的数据")


class DesensitizationRequest(BaseModel):
    """脱敏请求"""
    data: Dict[str, Any] = Field(..., description="待脱敏数据")
    asset_ids: Optional[List[int]] = Field(None, description="数据资产ID列表")


class DesensitizationResponse(BaseModel):
    """脱敏响应"""
    original_data: Dict[str, Any] = Field(..., description="原始数据")
    desensitized_data: Dict[str, Any] = Field(..., description="脱敏后的数据")
    desensitized_fields: List[str] = Field(default_factory=list, description="被脱敏的字段列表")

