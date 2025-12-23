"""
数据脱敏引擎
作者：张彦龙
"""
from typing import Dict, Any, List
import re
import hashlib


class DesensitizationEngine:
    """数据脱敏引擎"""
    
    def __init__(self, db=None):
        # 敏感字段识别规则
        self.sensitive_fields = {
            "身份证": r"ID_NO|IDNO|身份证|IDCARD",
            "手机号": r"MOB_NO|MOBILE|手机|PHONE",
            "银行卡": r"CARD_NO|ACCT_NO|银行卡|ACCOUNT",
            "姓名": r"CUST_NM|CUSTOMER_NAME|姓名|NAME",
            "邮箱": r"EMAIL|邮箱"
        }
        self.db = db
        if db:
            from app.utils.config_helper import ConfigHelper
            self.config_helper = ConfigHelper(db)
        else:
            self.config_helper = None
    
    def desensitize(self, data: Dict[str, Any], asset_ids: List[int] = None) -> Dict[str, Any]:
        """对数据进行脱敏处理"""
        # 检查脱敏功能是否启用
        if self.config_helper:
            if not self.config_helper.get_desensitization_enabled():
                return data  # 脱敏功能未启用，返回原始数据
        
        desensitized = {}
        
        for key, value in data.items():
            if value is None:
                desensitized[key] = value
                continue
            
            # 检查字段名是否匹配敏感字段规则
            is_sensitive = False
            field_type = None
            
            for field_type_name, pattern in self.sensitive_fields.items():
                if re.search(pattern, key, re.IGNORECASE):
                    is_sensitive = True
                    field_type = field_type_name
                    break
            
            if is_sensitive:
                desensitized[key] = self._apply_desensitization(value, field_type)
            elif isinstance(value, dict):
                desensitized[key] = self.desensitize(value, asset_ids)
            elif isinstance(value, list):
                desensitized[key] = [
                    self.desensitize(item, asset_ids) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                desensitized[key] = value
        
        return desensitized
    
    def _apply_desensitization(self, value: Any, field_type: str) -> str:
        """应用脱敏规则"""
        if not isinstance(value, str):
            value = str(value)
        
        if field_type == "身份证":
            # 身份证：保留前3位和后4位，中间用*代替
            if len(value) >= 7:
                return value[:3] + "*" * (len(value) - 7) + value[-4:]
            return "*" * len(value)
        
        elif field_type == "手机号":
            # 手机号：保留前3位和后4位
            if len(value) >= 7:
                return value[:3] + "****" + value[-4:]
            return "****"
        
        elif field_type == "银行卡":
            # 银行卡：保留后4位
            if len(value) >= 4:
                return "****" + value[-4:]
            return "****"
        
        elif field_type == "姓名":
            # 姓名：假名化（使用哈希）
            return self._pseudonymize(value)
        
        elif field_type == "邮箱":
            # 邮箱：保留@前的前2位和后1位
            if "@" in value:
                parts = value.split("@")
                if len(parts[0]) >= 3:
                    masked = parts[0][:2] + "*" * (len(parts[0]) - 3) + parts[0][-1]
                    return f"{masked}@{parts[1]}"
            return "***@***"
        
        # 默认：遮掩中间部分
        if len(value) > 4:
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        return "*" * len(value)
    
    def _pseudonymize(self, value: str) -> str:
        """假名化处理（生成唯一标识符）"""
        # 使用SHA256生成哈希，取前8位作为假名
        hash_obj = hashlib.sha256(value.encode())
        return f"UID_{hash_obj.hexdigest()[:8]}"

