"""
系统配置Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from app.models.system_config import ConfigCategory, ConfigType


class SystemConfigBase(BaseModel):
    """系统配置基础模型"""
    config_key: str = Field(..., description="配置键（唯一）")
    config_name: str = Field(..., description="配置名称")
    config_value: str = Field(..., description="配置值")
    config_type: ConfigType = Field(ConfigType.STRING, description="配置值类型")
    category: ConfigCategory = Field(..., description="配置分类")
    description: Optional[str] = Field(None, description="配置描述")
    is_encrypted: bool = Field(False, description="是否加密存储")
    is_editable: bool = Field(True, description="是否可编辑")
    is_public: bool = Field(False, description="是否公开（前端可访问）")
    validation_rule: Optional[str] = Field(None, description="验证规则（JSON格式）")
    default_value: Optional[str] = Field(None, description="默认值")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置"""
    pass


class SystemConfigUpdate(BaseModel):
    """更新系统配置"""
    config_value: Optional[str] = None
    description: Optional[str] = None
    is_editable: Optional[bool] = None
    is_public: Optional[bool] = None


class SystemConfigResponse(SystemConfigBase):
    """系统配置响应模型"""
    id: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConfigValueResponse(BaseModel):
    """配置值响应（用于前端获取公开配置）"""
    config_key: str
    config_value: Any
    config_type: str

