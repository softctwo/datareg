"""
系统配置服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
import json
from app.models.system_config import SystemConfig, ConfigCategory, ConfigType
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class SystemConfigService:
    """系统配置服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_configs(
        self,
        category: Optional[ConfigCategory] = None,
        is_public: Optional[bool] = None
    ) -> List[SystemConfig]:
        """获取配置列表"""
        query = self.db.query(SystemConfig)
        
        if category:
            query = query.filter(SystemConfig.category == category)
        if is_public is not None:
            query = query.filter(SystemConfig.is_public == is_public)
        
        return query.order_by(SystemConfig.category, SystemConfig.config_key).all()
    
    def get_config(self, config_id: int) -> Optional[SystemConfig]:
        """获取配置详情"""
        return self.db.query(SystemConfig).filter(SystemConfig.id == config_id).first()
    
    def get_config_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """根据配置键获取配置"""
        return self.db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    def create_config(self, config_data: SystemConfigCreate, updated_by: int) -> SystemConfig:
        """创建配置"""
        # 检查配置键是否已存在
        existing = self.get_config_by_key(config_data.config_key)
        if existing:
            raise ValueError(f"配置键 {config_data.config_key} 已存在")
        
        # 验证配置值类型
        value = config_data.config_value
        if config_data.config_type == ConfigType.INTEGER:
            try:
                int(value)
            except (ValueError, TypeError):
                raise ValueError(f"配置值必须是整数，当前值: {value}")
        elif config_data.config_type == ConfigType.FLOAT:
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValueError(f"配置值必须是浮点数，当前值: {value}")
        elif config_data.config_type == ConfigType.BOOLEAN:
            if str(value).lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
                raise ValueError(f"配置值必须是布尔值，当前值: {value}")
        elif config_data.config_type == ConfigType.JSON:
            if isinstance(value, str):
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    raise ValueError(f"配置值必须是有效的JSON格式，当前值: {value}")
        
        db_config = SystemConfig(**config_data.model_dump(), updated_by=updated_by)
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        return db_config
    
    def update_config(
        self,
        config_id: int,
        config_data: SystemConfigUpdate,
        updated_by: int
    ) -> Optional[SystemConfig]:
        """更新配置"""
        db_config = self.get_config(config_id)
        if not db_config:
            return None
        
        if not db_config.is_editable:
            raise ValueError("该配置不可编辑")
        
        update_data = config_data.model_dump(exclude_unset=True)
        
        # 如果更新了配置值，需要验证类型
        if 'config_value' in update_data:
            value = update_data['config_value']
            if db_config.config_type == ConfigType.INTEGER:
                try:
                    int(value)
                except (ValueError, TypeError):
                    raise ValueError(f"配置值必须是整数，当前值: {value}")
            elif db_config.config_type == ConfigType.FLOAT:
                try:
                    float(value)
                except (ValueError, TypeError):
                    raise ValueError(f"配置值必须是浮点数，当前值: {value}")
            elif db_config.config_type == ConfigType.BOOLEAN:
                if str(value).lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
                    raise ValueError(f"配置值必须是布尔值，当前值: {value}")
            elif db_config.config_type == ConfigType.JSON:
                if isinstance(value, str):
                    try:
                        json.loads(value)
                    except json.JSONDecodeError:
                        raise ValueError(f"配置值必须是有效的JSON格式，当前值: {value}")
        
        for field, value in update_data.items():
            setattr(db_config, field, value)
        
        db_config.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_config)
        return db_config
    
    def delete_config(self, config_id: int) -> bool:
        """删除配置"""
        db_config = self.get_config(config_id)
        if not db_config:
            return False
        
        if not db_config.is_editable:
            raise ValueError("该配置不可删除")
        
        self.db.delete(db_config)
        self.db.commit()
        return True
    
    def get_config_value(self, config_key: str, default: Any = None) -> Any:
        """获取配置值（自动类型转换）"""
        config = self.get_config_by_key(config_key)
        if not config:
            return default
        
        value = config.config_value
        
        # 根据类型转换
        if config.config_type == ConfigType.INTEGER:
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif config.config_type == ConfigType.FLOAT:
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        elif config.config_type == ConfigType.BOOLEAN:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif config.config_type == ConfigType.JSON:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return default
        else:
            return value
    
    def get_public_configs(self) -> Dict[str, Any]:
        """获取所有公开配置（用于前端）"""
        configs = self.list_configs(is_public=True)
        result = {}
        for config in configs:
            result[config.config_key] = self.get_config_value(config.config_key)
        return result
    
    def set_config_value(self, config_key: str, value: Any, updated_by: int) -> bool:
        """设置配置值"""
        config = self.get_config_by_key(config_key)
        if not config:
            return False
        
        if not config.is_editable:
            raise ValueError("该配置不可编辑")
        
        # 验证值是否符合类型
        if config.config_type == ConfigType.INTEGER:
            try:
                int(value)
            except (ValueError, TypeError):
                raise ValueError(f"配置值必须是整数，当前值: {value}")
        elif config.config_type == ConfigType.FLOAT:
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValueError(f"配置值必须是浮点数，当前值: {value}")
        elif config.config_type == ConfigType.BOOLEAN:
            if str(value).lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
                raise ValueError(f"配置值必须是布尔值，当前值: {value}")
        elif config.config_type == ConfigType.JSON:
            if isinstance(value, str):
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    raise ValueError(f"配置值必须是有效的JSON格式，当前值: {value}")
            else:
                value = json.dumps(value, ensure_ascii=False)
        
        # 根据类型转换值
        if config.config_type == ConfigType.JSON:
            if isinstance(value, str):
                config.config_value = value
            else:
                config.config_value = json.dumps(value, ensure_ascii=False)
        else:
            config.config_value = str(value)
        
        config.updated_by = updated_by
        self.db.commit()
        return True

