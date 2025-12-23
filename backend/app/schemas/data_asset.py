"""
数据资产Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.data_asset import DataLevel


class DataAssetBase(BaseModel):
    """数据资产基础模型"""
    asset_name: str = Field(..., description="资产名称")
    asset_code: str = Field(..., description="资产编码")
    asset_type: Optional[str] = Field(None, description="资产类型")
    source_system: Optional[str] = Field(None, description="来源系统")
    schema_name: Optional[str] = Field(None, description="数据库Schema")
    table_name: Optional[str] = Field(None, description="表名")
    description: Optional[str] = Field(None, description="描述")


class DataAssetCreate(DataAssetBase):
    """创建数据资产"""
    data_level: DataLevel = Field(DataLevel.INTERNAL, description="数据安全级别")
    classification_id: Optional[int] = Field(None, description="分类ID")


class DataAssetUpdate(BaseModel):
    """更新数据资产"""
    asset_name: Optional[str] = None
    description: Optional[str] = None
    data_level: Optional[DataLevel] = None
    classification_id: Optional[int] = None
    is_active: Optional[bool] = None


class DataAssetResponse(DataAssetBase):
    """数据资产响应模型"""
    id: int
    data_level: DataLevel
    classification_id: Optional[int]
    field_count: Optional[int]
    record_count: Optional[int]
    is_active: bool
    last_scan_time: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DataClassificationBase(BaseModel):
    """数据分类基础模型"""
    category_name: str
    category_code: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class DataClassificationCreate(DataClassificationBase):
    """创建数据分类"""
    pass


class DataClassificationResponse(DataClassificationBase):
    """数据分类响应模型"""
    id: int
    level: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SensitiveTagBase(BaseModel):
    """敏感标签基础模型"""
    tag_name: str
    tag_code: str
    tag_type: Optional[str] = None
    detection_rule: Optional[str] = None
    risk_level: Optional[str] = None
    description: Optional[str] = None


class SensitiveTagCreate(SensitiveTagBase):
    """创建敏感标签"""
    pass


class SensitiveTagResponse(SensitiveTagBase):
    """敏感标签响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LineageNode(BaseModel):
    """血缘关系节点"""
    id: int
    name: str
    code: str
    type: Optional[str] = None
    data_level: str
    
    class Config:
        from_attributes = True


class LineageEdge(BaseModel):
    """血缘关系边"""
    source: int
    target: int
    type: str = Field("upstream", description="关系类型：upstream/downstream")
    
    class Config:
        from_attributes = True


class LineageGraph(BaseModel):
    """血缘关系图"""
    nodes: List[LineageNode]
    edges: List[LineageEdge]
    center_node_id: int

