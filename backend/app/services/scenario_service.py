"""
跨境传输场景服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.scenario import CrossBorderScenario, ScenarioStatus
from app.schemas.scenario import CrossBorderScenarioCreate, CrossBorderScenarioUpdate


class ScenarioService:
    """跨境传输场景服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_scenarios(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        recipient_country: Optional[str] = None
    ) -> List[CrossBorderScenario]:
        """获取场景列表"""
        query = self.db.query(CrossBorderScenario)
        
        if status:
            query = query.filter(CrossBorderScenario.status == status)
        if recipient_country:
            query = query.filter(CrossBorderScenario.recipient_country == recipient_country)
        
        return query.offset(skip).limit(limit).all()
    
    def get_scenario(self, scenario_id: int) -> Optional[CrossBorderScenario]:
        """获取场景详情"""
        return self.db.query(CrossBorderScenario).filter(
            CrossBorderScenario.id == scenario_id
        ).first()
    
    def create_scenario(self, scenario_data: CrossBorderScenarioCreate) -> CrossBorderScenario:
        """创建场景"""
        db_scenario = CrossBorderScenario(**scenario_data.model_dump())
        db_scenario.status = ScenarioStatus.DRAFT
        self.db.add(db_scenario)
        self.db.commit()
        self.db.refresh(db_scenario)
        return db_scenario
    
    def update_scenario(
        self,
        scenario_id: int,
        scenario_data: CrossBorderScenarioUpdate
    ) -> Optional[CrossBorderScenario]:
        """更新场景"""
        db_scenario = self.get_scenario(scenario_id)
        if not db_scenario:
            return None
        
        # 只有草稿状态才能更新
        if db_scenario.status != ScenarioStatus.DRAFT:
            raise ValueError("只有草稿状态的场景才能更新")
        
        update_data = scenario_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_scenario, field, value)
        
        self.db.commit()
        self.db.refresh(db_scenario)
        return db_scenario
    
    def submit_for_approval(self, scenario_id: int) -> Optional[CrossBorderScenario]:
        """提交场景审批"""
        db_scenario = self.get_scenario(scenario_id)
        if not db_scenario:
            return None
        
        if db_scenario.status != ScenarioStatus.DRAFT:
            raise ValueError("只有草稿状态的场景才能提交审批")
        
        db_scenario.status = ScenarioStatus.PENDING
        self.db.commit()
        self.db.refresh(db_scenario)
        return db_scenario
    
    def approve_scenario(
        self,
        scenario_id: int,
        approver_id: int,
        comment: Optional[str] = None
    ) -> Optional[CrossBorderScenario]:
        """批准场景"""
        db_scenario = self.get_scenario(scenario_id)
        if not db_scenario:
            return None
        
        if db_scenario.status != ScenarioStatus.PENDING:
            raise ValueError("只有待审批状态的场景才能批准")
        
        db_scenario.status = ScenarioStatus.APPROVED
        db_scenario.approver_id = approver_id
        db_scenario.approved_at = datetime.now()
        # 默认有效期1年
        db_scenario.expiry_date = datetime.now() + timedelta(days=365)
        
        self.db.commit()
        self.db.refresh(db_scenario)
        return db_scenario
    
    def reject_scenario(
        self,
        scenario_id: int,
        approver_id: int,
        reason: str
    ) -> Optional[CrossBorderScenario]:
        """拒绝场景"""
        db_scenario = self.get_scenario(scenario_id)
        if not db_scenario:
            return None
        
        if db_scenario.status != ScenarioStatus.PENDING:
            raise ValueError("只有待审批状态的场景才能拒绝")
        
        db_scenario.status = ScenarioStatus.REJECTED
        db_scenario.approver_id = approver_id
        
        self.db.commit()
        self.db.refresh(db_scenario)
        return db_scenario

