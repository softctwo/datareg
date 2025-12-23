"""
传输审批服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.scenario import TransferApproval, ApprovalStatus
from app.schemas.approval import TransferApprovalCreate, TransferApprovalUpdate
from app.services.interception_service import InterceptionService
from app.utils.config_helper import ConfigHelper


class ApprovalService:
    """传输审批服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.interception_service = InterceptionService(db)
        self.config_helper = ConfigHelper(db)
    
    def list_approvals(
        self,
        skip: int = 0,
        limit: int = 100,
        scenario_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[TransferApproval]:
        """获取传输审批列表"""
        query = self.db.query(TransferApproval)
        
        if scenario_id:
            query = query.filter(TransferApproval.scenario_id == scenario_id)
        if status:
            query = query.filter(TransferApproval.approval_status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_approval(self, approval_id: int) -> Optional[TransferApproval]:
        """获取审批详情"""
        return self.db.query(TransferApproval).filter(
            TransferApproval.id == approval_id
        ).first()
    
    def create_approval(self, approval_data: TransferApprovalCreate) -> TransferApproval:
        """创建传输审批申请"""
        # 将data_assets列表转为JSON字符串
        approval_dict = approval_data.model_dump()
        if approval_dict.get("data_assets"):
            import json
            approval_dict["data_assets"] = json.dumps(approval_dict["data_assets"])
        
        db_approval = TransferApproval(**approval_dict)
        db_approval.approval_status = ApprovalStatus.PENDING
        self.db.add(db_approval)
        self.db.commit()
        self.db.refresh(db_approval)
        return db_approval
    
    def approve_transfer(
        self,
        approval_id: int,
        approver_id: int,
        comment: Optional[str] = None,
        risk_score: Optional[int] = None
    ) -> Optional[TransferApproval]:
        """批准传输"""
        db_approval = self.get_approval(approval_id)
        if not db_approval:
            return None
        
        if db_approval.approval_status != ApprovalStatus.PENDING:
            raise ValueError("只有待审批状态的申请才能批准")
        
        # 检查是否需要多级审批
        if self.config_helper.get_require_multi_level() and risk_score:
            multi_level_threshold = self.config_helper.get_multi_level_risk_threshold()
            if risk_score >= multi_level_threshold:
                # 需要多级审批，这里可以扩展逻辑
                pass
        
        db_approval.approval_status = ApprovalStatus.APPROVED
        db_approval.approver_id = approver_id
        db_approval.approval_comment = comment
        db_approval.approved_at = datetime.now()
        
        # 在拦截服务中注册白名单
        self.interception_service.add_to_whitelist(db_approval)
        
        self.db.commit()
        self.db.refresh(db_approval)
        return db_approval
    
    def reject_transfer(
        self,
        approval_id: int,
        approver_id: int,
        reason: str
    ) -> Optional[TransferApproval]:
        """拒绝传输"""
        db_approval = self.get_approval(approval_id)
        if not db_approval:
            return None
        
        if db_approval.approval_status != ApprovalStatus.PENDING:
            raise ValueError("只有待审批状态的申请才能拒绝")
        
        db_approval.approval_status = ApprovalStatus.REJECTED
        db_approval.approver_id = approver_id
        db_approval.rejected_reason = reason
        
        self.db.commit()
        self.db.refresh(db_approval)
        return db_approval

