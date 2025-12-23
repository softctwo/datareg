"""
数据资产服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Set, Tuple
from datetime import datetime
import json
from app.models.data_asset import DataAsset, DataClassification, SensitiveTag, DataLevel
from app.schemas.data_asset import (
    DataAssetCreate, DataAssetUpdate,
    DataClassificationCreate, SensitiveTagCreate,
    LineageNode, LineageEdge, LineageGraph
)
from app.utils.data_scanner import DataScanner
from app.utils.classification_engine import ClassificationEngine


class DataAssetService:
    """数据资产服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scanner = DataScanner(db)
        self.classifier = ClassificationEngine(db)
    
    def list_assets(
        self,
        skip: int = 0,
        limit: int = 100,
        data_level: Optional[str] = None,
        source_system: Optional[str] = None,
        asset_name: Optional[str] = None,
        asset_code: Optional[str] = None,
        asset_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> tuple[List[DataAsset], int]:
        """获取数据资产列表（支持高级搜索）"""
        query = self.db.query(DataAsset)
        
        # 精确匹配筛选
        if data_level:
            query = query.filter(DataAsset.data_level == data_level)
        if source_system:
            query = query.filter(DataAsset.source_system == source_system)
        if asset_type:
            query = query.filter(DataAsset.asset_type == asset_type)
        if is_active is not None:
            query = query.filter(DataAsset.is_active == is_active)
        
        # 模糊搜索
        if asset_name:
            query = query.filter(DataAsset.asset_name.ilike(f"%{asset_name}%"))
        if asset_code:
            query = query.filter(DataAsset.asset_code.ilike(f"%{asset_code}%"))
        
        # 通用搜索（搜索名称、编码、描述）
        if search:
            query = query.filter(
                or_(
                    DataAsset.asset_name.ilike(f"%{search}%"),
                    DataAsset.asset_code.ilike(f"%{search}%"),
                    DataAsset.description.ilike(f"%{search}%")
                )
            )
        
        # 日期范围筛选
        if created_from:
            query = query.filter(DataAsset.created_at >= created_from)
        if created_to:
            query = query.filter(DataAsset.created_at <= created_to)
        
        # 获取总数
        total = query.count()
        
        # 分页
        assets = query.order_by(DataAsset.created_at.desc()).offset(skip).limit(limit).all()
        
        return assets, total
    
    def get_asset(self, asset_id: int) -> Optional[DataAsset]:
        """获取数据资产详情"""
        return self.db.query(DataAsset).filter(DataAsset.id == asset_id).first()
    
    def create_asset(self, asset_data: DataAssetCreate) -> DataAsset:
        """创建数据资产"""
        db_asset = DataAsset(**asset_data.model_dump())
        self.db.add(db_asset)
        self.db.commit()
        self.db.refresh(db_asset)
        return db_asset
    
    def update_asset(self, asset_id: int, asset_data: DataAssetUpdate) -> Optional[DataAsset]:
        """更新数据资产"""
        db_asset = self.get_asset(asset_id)
        if not db_asset:
            return None
        
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_asset, field, value)
        
        self.db.commit()
        self.db.refresh(db_asset)
        return db_asset
    
    def scan_and_classify(self, source_system: Optional[str] = None) -> dict:
        """扫描数据资产并自动分类分级"""
        # 扫描元数据
        scanned_assets = self.scanner.scan_metadata(source_system)
        
        # 自动分类分级
        classified_count = 0
        for asset in scanned_assets:
            # 使用分类引擎进行自动识别
            classification_result = self.classifier.classify_asset(asset)
            if classification_result:
                asset.data_level = classification_result.get("data_level", DataLevel.INTERNAL)
                asset.classification_id = classification_result.get("classification_id")
                classified_count += 1
        
        self.db.commit()
        
        return {
            "count": len(scanned_assets),
            "classified_count": classified_count
        }
    
    def list_classifications(self) -> List[DataClassification]:
        """获取数据分类列表"""
        return self.db.query(DataClassification).all()
    
    def create_classification(self, classification_data: DataClassificationCreate) -> DataClassification:
        """创建数据分类"""
        db_classification = DataClassification(**classification_data.model_dump())
        self.db.add(db_classification)
        self.db.commit()
        self.db.refresh(db_classification)
        return db_classification
    
    def list_tags(self) -> List[SensitiveTag]:
        """获取敏感标签列表"""
        return self.db.query(SensitiveTag).filter(SensitiveTag.is_active == True).all()
    
    def create_tag(self, tag_data: SensitiveTagCreate) -> SensitiveTag:
        """创建敏感标签"""
        db_tag = SensitiveTag(**tag_data.model_dump())
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag
    
    def get_lineage_graph(self, asset_id: int, depth: int = 2) -> LineageGraph:
        """获取数据资产的血缘关系图"""
        center_asset = self.get_asset(asset_id)
        if not center_asset:
            raise ValueError(f"数据资产 {asset_id} 不存在")
        
        # 收集所有相关资产ID
        asset_ids: Set[int] = {asset_id}
        nodes: Dict[int, DataAsset] = {asset_id: center_asset}
        edges: List[LineageEdge] = []
        
        # 递归收集上游和下游资产
        def collect_related_assets(current_id: int, current_depth: int):
            if current_depth > depth:
                return
            
            asset = nodes.get(current_id)
            if not asset:
                return
            
            # 收集上游资产
            if asset.upstream_assets:
                try:
                    upstream_ids = json.loads(asset.upstream_assets)
                    if isinstance(upstream_ids, list):
                        for upstream_id in upstream_ids:
                            if upstream_id not in asset_ids:
                                upstream_asset = self.get_asset(upstream_id)
                                if upstream_asset:
                                    asset_ids.add(upstream_id)
                                    nodes[upstream_id] = upstream_asset
                                    edges.append(LineageEdge(
                                        source=upstream_id,
                                        target=current_id,
                                        type="downstream"
                                    ))
                                    collect_related_assets(upstream_id, current_depth + 1)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # 收集下游资产
            if asset.downstream_assets:
                try:
                    downstream_ids = json.loads(asset.downstream_assets)
                    if isinstance(downstream_ids, list):
                        for downstream_id in downstream_ids:
                            if downstream_id not in asset_ids:
                                downstream_asset = self.get_asset(downstream_id)
                                if downstream_asset:
                                    asset_ids.add(downstream_id)
                                    nodes[downstream_id] = downstream_asset
                                    edges.append(LineageEdge(
                                        source=current_id,
                                        target=downstream_id,
                                        type="downstream"
                                    ))
                                    collect_related_assets(downstream_id, current_depth + 1)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        collect_related_assets(asset_id, 0)
        
        # 转换为响应模型
        lineage_nodes = [
            LineageNode(
                id=node.id,
                name=node.asset_name,
                code=node.asset_code,
                type=node.asset_type,
                data_level=node.data_level.value
            )
            for node in nodes.values()
        ]
        
        return LineageGraph(
            nodes=lineage_nodes,
            edges=edges,
            center_node_id=asset_id
        )

