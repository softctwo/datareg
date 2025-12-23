"""
数据资产模型
作者：张彦龙
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DataLevel(str, enum.Enum):
    """数据安全级别"""
    CORE = "核心数据"  # 涉及国家安全
    IMPORTANT = "重要数据"  # 重要数据
    SENSITIVE = "敏感个人信息"  # 敏感个人信息
    PERSONAL = "个人信息"  # 一般个人信息
    INTERNAL = "内部数据"  # 内部数据
    PUBLIC = "公开数据"  # 公开数据


class DataAsset(Base):
    """数据资产表"""
    __tablename__ = "data_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String(200), nullable=False, index=True, comment="资产名称")
    asset_code = Column(String(100), unique=True, nullable=False, index=True, comment="资产编码")
    asset_type = Column(String(50), comment="资产类型：表/视图/接口/文件")
    source_system = Column(String(100), comment="来源系统")
    schema_name = Column(String(100), comment="数据库Schema")
    table_name = Column(String(200), comment="表名")
    
    # 分类分级信息
    data_level = Column(SQLEnum(DataLevel), nullable=False, default=DataLevel.INTERNAL, comment="数据安全级别")
    classification_id = Column(Integer, ForeignKey("data_classifications.id"), comment="分类ID")
    
    # 元数据
    description = Column(Text, comment="描述")
    field_count = Column(Integer, comment="字段数量")
    record_count = Column(Integer, comment="记录数（估算）")
    
    # 血缘关系
    upstream_assets = Column(Text, comment="上游资产（JSON）")
    downstream_assets = Column(Text, comment="下游资产（JSON）")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    last_scan_time = Column(DateTime(timezone=True), comment="最后扫描时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    classification = relationship("DataClassification", back_populates="assets")
    sensitive_tags = relationship("SensitiveTag", secondary="asset_tag_association", back_populates="assets")


class DataClassification(Base):
    """数据分类表"""
    __tablename__ = "data_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False, comment="分类名称")
    category_code = Column(String(50), unique=True, nullable=False, comment="分类编码")
    parent_id = Column(Integer, ForeignKey("data_classifications.id"), comment="父分类ID")
    level = Column(Integer, default=1, comment="分类层级")
    description = Column(Text, comment="描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    assets = relationship("DataAsset", back_populates="classification")
    children = relationship("DataClassification", backref="parent", remote_side=[id])


class SensitiveTag(Base):
    """敏感标签表"""
    __tablename__ = "sensitive_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(100), unique=True, nullable=False, comment="标签名称")
    tag_code = Column(String(50), unique=True, nullable=False, comment="标签编码")
    tag_type = Column(String(50), comment="标签类型：PII/重要数据/核心数据")
    detection_rule = Column(Text, comment="识别规则（正则表达式或规则描述）")
    risk_level = Column(String(20), comment="风险等级：高/中/低")
    description = Column(Text, comment="描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    assets = relationship("DataAsset", secondary="asset_tag_association", back_populates="sensitive_tags")


# 资产标签关联表
from sqlalchemy import Table
asset_tag_association = Table(
    'asset_tag_association',
    Base.metadata,
    Column('asset_id', Integer, ForeignKey('data_assets.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('sensitive_tags.id'), primary_key=True)
)

