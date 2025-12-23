"""
数据资产API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.database import get_db
from app.models.data_asset import DataAsset, DataClassification, SensitiveTag
from app.schemas.data_asset import (
    DataAssetCreate, DataAssetUpdate, DataAssetResponse,
    DataClassificationCreate, DataClassificationResponse,
    SensitiveTagCreate, SensitiveTagResponse,
    LineageGraph
)
from app.services.data_asset_service import DataAssetService

router = APIRouter()


class DataAssetListResponse(BaseModel):
    """数据资产列表响应（包含总数）"""
    items: List[DataAssetResponse]
    total: int
    skip: int
    limit: int


@router.get("/", response_model=DataAssetListResponse)
async def list_data_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    data_level: Optional[str] = None,
    source_system: Optional[str] = None,
    asset_name: Optional[str] = None,
    asset_code: Optional[str] = None,
    asset_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    created_from: Optional[datetime] = Query(None, description="创建时间起始"),
    created_to: Optional[datetime] = Query(None, description="创建时间结束"),
    search: Optional[str] = Query(None, description="通用搜索（名称、编码、描述）"),
    db: Session = Depends(get_db)
):
    """获取数据资产列表（支持高级搜索）"""
    service = DataAssetService(db)
    assets, total = service.list_assets(
        skip=skip,
        limit=limit,
        data_level=data_level,
        source_system=source_system,
        asset_name=asset_name,
        asset_code=asset_code,
        asset_type=asset_type,
        is_active=is_active,
        created_from=created_from,
        created_to=created_to,
        search=search
    )
    return DataAssetListResponse(items=assets, total=total, skip=skip, limit=limit)


@router.get("/{asset_id}", response_model=DataAssetResponse)
async def get_data_asset(asset_id: int, db: Session = Depends(get_db)):
    """获取数据资产详情"""
    service = DataAssetService(db)
    asset = service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="数据资产不存在")
    return asset


@router.post("/", response_model=DataAssetResponse)
async def create_data_asset(asset: DataAssetCreate, db: Session = Depends(get_db)):
    """创建数据资产"""
    service = DataAssetService(db)
    return service.create_asset(asset)


@router.put("/{asset_id}", response_model=DataAssetResponse)
async def update_data_asset(asset_id: int, asset: DataAssetUpdate, db: Session = Depends(get_db)):
    """更新数据资产"""
    service = DataAssetService(db)
    updated = service.update_asset(asset_id, asset)
    if not updated:
        raise HTTPException(status_code=404, detail="数据资产不存在")
    return updated


@router.post("/scan", response_model=dict)
async def scan_data_assets(
    source_system: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """扫描数据资产（元数据扫描和自动打标）"""
    service = DataAssetService(db)
    result = service.scan_and_classify(source_system)
    return {"message": "扫描完成", "scanned_count": result.get("count", 0)}


@router.get("/classifications/", response_model=List[DataClassificationResponse])
async def list_classifications(db: Session = Depends(get_db)):
    """获取数据分类列表"""
    service = DataAssetService(db)
    return service.list_classifications()


@router.post("/classifications/", response_model=DataClassificationResponse)
async def create_classification(
    classification: DataClassificationCreate,
    db: Session = Depends(get_db)
):
    """创建数据分类"""
    service = DataAssetService(db)
    return service.create_classification(classification)


@router.get("/tags/", response_model=List[SensitiveTagResponse])
async def list_sensitive_tags(db: Session = Depends(get_db)):
    """获取敏感标签列表"""
    service = DataAssetService(db)
    return service.list_tags()


@router.post("/tags/", response_model=SensitiveTagResponse)
async def create_sensitive_tag(tag: SensitiveTagCreate, db: Session = Depends(get_db)):
    """创建敏感标签"""
    service = DataAssetService(db)
    return service.create_tag(tag)


@router.get("/{asset_id}/lineage", response_model=LineageGraph)
async def get_asset_lineage(
    asset_id: int,
    depth: int = Query(2, ge=1, le=5, description="血缘关系深度"),
    db: Session = Depends(get_db)
):
    """获取数据资产的血缘关系图"""
    service = DataAssetService(db)
    try:
        return service.get_lineage_graph(asset_id, depth)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

