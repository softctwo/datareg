"""
数据资产扫描器
作者：张彦龙
"""
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from typing import List, Optional
from app.models.data_asset import DataAsset
from app.core.database import engine


class DataScanner:
    """数据资产扫描器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def scan_metadata(self, source_system: Optional[str] = None) -> List[DataAsset]:
        """扫描数据库元数据"""
        scanned_assets = []
        
        try:
            # 查询所有表
            inspector = inspect(engine)
            schemas = inspector.get_schema_names()
            
            for schema in schemas:
                if schema in ['information_schema', 'pg_catalog']:
                    continue
                
                tables = inspector.get_table_names(schema=schema)
                
                for table_name in tables:
                    # 检查资产是否已存在
                    existing_asset = self.db.query(DataAsset).filter(
                        DataAsset.schema_name == schema,
                        DataAsset.table_name == table_name
                    ).first()
                    
                    if existing_asset:
                        continue
                    
                    # 获取表信息
                    columns = inspector.get_columns(table_name, schema=schema)
                    
                    # 创建数据资产
                    asset = DataAsset(
                        asset_name=f"{schema}.{table_name}",
                        asset_code=f"{schema}_{table_name}".upper(),
                        asset_type="表",
                        source_system=source_system or "未知",
                        schema_name=schema,
                        table_name=table_name,
                        field_count=len(columns),
                        description=f"自动扫描发现的表：{schema}.{table_name}"
                    )
                    
                    self.db.add(asset)
                    scanned_assets.append(asset)
        
        except Exception as e:
            print(f"扫描元数据时出错: {e}")
        
        self.db.commit()
        return scanned_assets

