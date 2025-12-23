"""
数据分类分级引擎
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.models.data_asset import DataAsset, DataLevel, SensitiveTag
from app.models.data_asset import DataClassification
import re


class ClassificationEngine:
    """数据分类分级引擎"""
    
    def __init__(self, db: Session):
        self.db = db
        self._load_detection_rules()
    
    def _load_detection_rules(self):
        """加载敏感标签识别规则"""
        self.tags = self.db.query(SensitiveTag).filter(
            SensitiveTag.is_active == True
        ).all()
        
        # 重要数据识别规则
        self.important_data_patterns = [
            r"信贷总量|风险暴露|NON_REL_EXPOSURE",
            r"跨境支付|清算规模",
            r"重点行业|关键客户",
            r"实际控制人|ACTUAL_CONTROLLER"
        ]
    
    def classify_asset(self, asset: DataAsset) -> Optional[Dict]:
        """对数据资产进行分类分级"""
        result = {
            "data_level": DataLevel.INTERNAL,
            "classification_id": None
        }
        
        # 检查表名和字段名
        asset_name_lower = asset.asset_name.lower()
        
        # 检查是否为核心数据
        if any(keyword in asset_name_lower for keyword in ["核心", "core", "国家安全"]):
            result["data_level"] = DataLevel.CORE
            return result
        
        # 检查是否为重要数据
        for pattern in self.important_data_patterns:
            if re.search(pattern, asset.asset_name, re.IGNORECASE):
                result["data_level"] = DataLevel.IMPORTANT
                break
        
        # 检查敏感个人信息
        sensitive_keywords = [
            "身份证|ID_NO|IDNO",
            "手机号|MOB_NO|MOBILE",
            "银行卡|CARD_NO|ACCT_NO",
            "客户名称|CUST_NM|CUSTOMER_NAME"
        ]
        
        for keyword in sensitive_keywords:
            if re.search(keyword, asset.asset_name, re.IGNORECASE):
                if result["data_level"] == DataLevel.INTERNAL:
                    result["data_level"] = DataLevel.SENSITIVE
                break
        
        # 检查一般个人信息
        personal_keywords = ["客户|CUST", "个人信息|PERSONAL"]
        if result["data_level"] == DataLevel.INTERNAL:
            for keyword in personal_keywords:
                if re.search(keyword, asset.asset_name, re.IGNORECASE):
                    result["data_level"] = DataLevel.PERSONAL
                    break
        
        return result

