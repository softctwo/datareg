"""
拦截与脱敏服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.scenario import TransferApproval
from app.models.data_asset import DataAsset, DataLevel
from app.utils.desensitization import DesensitizationEngine


class InterceptionService:
    """拦截与脱敏服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.desensitizer = DesensitizationEngine(db)
        # 白名单：存储已批准的传输申请ID（从数据库加载）
        self.whitelist: set = self._load_whitelist()
        # 黑名单：存储被禁止的数据资产ID（从数据库加载）
        self.blacklist: set = self._load_blacklist()
    
    def _load_whitelist(self) -> set:
        """从数据库加载白名单（已批准的审批）"""
        from app.models.scenario import TransferApproval, ApprovalStatus
        approved_approvals = self.db.query(TransferApproval).filter(
            TransferApproval.approval_status == ApprovalStatus.APPROVED
        ).all()
        return {approval.id for approval in approved_approvals}
    
    def _load_blacklist(self) -> set:
        """从数据库加载黑名单（从配置或标记中获取）"""
        # 从系统配置中加载黑名单资产ID
        # 格式：配置键为 "interception.blacklist"，值为JSON数组
        from app.services.system_config_service import SystemConfigService
        config_service = SystemConfigService(self.db)
        try:
            blacklist_config = config_service.get_config_by_key("interception.blacklist")
            if blacklist_config:
                import json
                asset_ids = json.loads(blacklist_config.config_value)
                return set(asset_ids) if isinstance(asset_ids, list) else set()
        except:
            pass
        return set()
    
    def add_to_whitelist(self, approval: TransferApproval):
        """添加到白名单"""
        self.whitelist.add(approval.id)
    
    def remove_from_whitelist(self, approval_id: int):
        """从白名单移除"""
        self.whitelist.discard(approval_id)
    
    def get_whitelist(self) -> set:
        """获取白名单"""
        return self.whitelist
    
    def get_blacklist(self) -> set:
        """获取黑名单"""
        return self.blacklist
    
    def add_to_blacklist(self, asset_id: int):
        """添加到黑名单"""
        self.blacklist.add(asset_id)
    
    def check_interception(
        self,
        approval_id: Optional[int],
        asset_ids: List[int],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查是否需要拦截"""
        result = {
            "allowed": False,
            "intercepted": False,
            "reason": None,
            "desensitized_data": None
        }
        
        # 检查是否在白名单中
        if approval_id and approval_id in self.whitelist:
            # 检查数据资产是否在黑名单中
            if any(asset_id in self.blacklist for asset_id in asset_ids):
                result["intercepted"] = True
                result["reason"] = "数据资产在黑名单中，禁止出境"
                return result
            
            # 检查是否为核心数据
            assets = self.db.query(DataAsset).filter(DataAsset.id.in_(asset_ids)).all()
            if any(asset.data_level == DataLevel.CORE for asset in assets):
                result["intercepted"] = True
                result["reason"] = "涉及核心数据，严禁出境"
                return result
            
            # 允许传输，但需要脱敏
            result["allowed"] = True
            result["desensitized_data"] = self.desensitizer.desensitize(data, asset_ids)
            return result
        
        # 未在白名单中，拦截
        result["intercepted"] = True
        result["reason"] = "传输申请未批准或已过期"
        return result
    
    def intercept_transfer(
        self,
        approval_id: Optional[int],
        asset_ids: List[int],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """拦截传输并返回处理结果"""
        return self.check_interception(approval_id, asset_ids, data)

