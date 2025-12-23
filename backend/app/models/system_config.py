"""
系统配置模型
作者：张彦龙
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ConfigCategory(str, enum.Enum):
    """配置分类"""
    THRESHOLD = "阈值配置"  # 合规阈值配置
    DESENSITIZATION = "脱敏规则"  # 脱敏规则配置
    APPROVAL = "审批流程"  # 审批流程配置
    NOTIFICATION = "通知设置"  # 通知设置
    SYSTEM = "系统设置"  # 系统设置
    COMPLIANCE = "合规规则"  # 合规规则配置


class ConfigType(str, enum.Enum):
    """配置值类型"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="配置键（唯一）")
    config_name = Column(String(200), nullable=False, comment="配置名称")
    config_value = Column(Text, nullable=False, comment="配置值")
    config_type = Column(SQLEnum(ConfigType), default=ConfigType.STRING, comment="配置值类型")
    category = Column(SQLEnum(ConfigCategory), nullable=False, comment="配置分类")
    description = Column(Text, comment="配置描述")
    is_encrypted = Column(Boolean, default=False, comment="是否加密存储")
    is_editable = Column(Boolean, default=True, comment="是否可编辑")
    is_public = Column(Boolean, default=False, comment="是否公开（前端可访问）")
    validation_rule = Column(Text, comment="验证规则（JSON格式）")
    default_value = Column(Text, comment="默认值")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), comment="最后更新人")

