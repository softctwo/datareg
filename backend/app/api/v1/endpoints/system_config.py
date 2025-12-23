"""
系统配置API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.models.system_config import ConfigCategory, ConfigType
from app.schemas.system_config import (
    SystemConfigCreate, SystemConfigUpdate, SystemConfigResponse, ConfigValueResponse
)
from app.services.system_config_service import SystemConfigService
from app.core.permissions import get_current_user_id, require_permission

router = APIRouter()


@router.get("/", response_model=List[SystemConfigResponse])
async def list_configs(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_permission("config:read"))
):
    """获取系统配置列表"""
    service = SystemConfigService(db)
    config_category = None
    if category:
        try:
            config_category = ConfigCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的配置分类: {category}")
    
    return service.list_configs(category=config_category, is_public=is_public)


@router.get("/public", response_model=Dict[str, Any])
async def get_public_configs(db: Session = Depends(get_db)):
    """获取公开配置（前端可访问，无需权限）"""
    service = SystemConfigService(db)
    return service.get_public_configs()


@router.get("/{config_id}", response_model=SystemConfigResponse)
async def get_config(
    config_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_permission("config:read"))
):
    """获取配置详情"""
    service = SystemConfigService(db)
    config = service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.get("/key/{config_key}", response_model=ConfigValueResponse)
async def get_config_by_key(
    config_key: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_permission("config:read"))
):
    """根据配置键获取配置值"""
    service = SystemConfigService(db)
    config = service.get_config_by_key(config_key)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return ConfigValueResponse(
        config_key=config.config_key,
        config_value=service.get_config_value(config_key),
        config_type=config.config_type.value
    )


@router.post("/", response_model=SystemConfigResponse)
async def create_config(
    config: SystemConfigCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_permission("config:write"))
):
    """创建系统配置"""
    service = SystemConfigService(db)
    try:
        return service.create_config(config, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{config_id}", response_model=SystemConfigResponse)
async def update_config(
    config_id: int,
    config: SystemConfigUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_permission("config:write"))
):
    """更新系统配置"""
    service = SystemConfigService(db)
    try:
        updated = service.update_config(config_id, config, user_id)
        if not updated:
            raise HTTPException(status_code=404, detail="配置不存在")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/key/{config_key}/value", response_model=dict)
async def set_config_value(
    config_key: str,
    value: str = Query(..., description="配置值"),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_permission("config:write"))
):
    """设置配置值"""
    service = SystemConfigService(db)
    try:
        success = service.set_config_value(config_key, value, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {"message": "配置值已更新", "config_key": config_key}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}", response_model=dict)
async def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_permission("config:delete"))
):
    """删除系统配置"""
    service = SystemConfigService(db)
    try:
        success = service.delete_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {"message": "配置已删除"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

