"""
风险评估服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.models.risk import RiskAssessment, RiskLevel, AssessmentStatus
from app.schemas.risk import RiskAssessmentCreate, RiskAssessmentUpdate
from app.core.config import settings
from app.utils.config_helper import ConfigHelper


class RiskAssessmentService:
    """风险评估服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_helper = ConfigHelper(db)
    
    def list_assessments(
        self,
        skip: int = 0,
        limit: int = 100,
        scenario_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[RiskAssessment]:
        """获取风险评估列表"""
        query = self.db.query(RiskAssessment)
        
        if scenario_id:
            query = query.filter(RiskAssessment.scenario_id == scenario_id)
        if status:
            # 将字符串状态转换为Enum
            from app.models.risk import AssessmentStatus
            try:
                status_enum = AssessmentStatus(status)
                query = query.filter(RiskAssessment.status == status_enum)
            except ValueError:
                pass  # 无效的状态值，忽略过滤
        
        return query.offset(skip).limit(limit).all()
    
    def get_assessment(self, assessment_id: int) -> Optional[RiskAssessment]:
        """获取风险评估详情"""
        return self.db.query(RiskAssessment).filter(
            RiskAssessment.id == assessment_id
        ).first()
    
    def create_assessment(self, assessment_data: RiskAssessmentCreate) -> RiskAssessment:
        """创建风险评估"""
        db_assessment = RiskAssessment(**assessment_data.model_dump())
        db_assessment.status = AssessmentStatus.DRAFT
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        return db_assessment
    
    def calculate_risk(self, assessment_id: int) -> Optional[RiskAssessment]:
        """执行风险评估计算"""
        db_assessment = self.get_assessment(assessment_id)
        if not db_assessment:
            return None
        
        # 计算综合评分（加权平均）
        scores = []
        weights = []
        
        if db_assessment.legal_environment_score:
            scores.append(float(db_assessment.legal_environment_score))
            weights.append(0.3)
        
        if db_assessment.data_volume_score:
            scores.append(float(db_assessment.data_volume_score))
            weights.append(0.25)
        
        if db_assessment.security_measures_score:
            scores.append(float(db_assessment.security_measures_score))
            weights.append(0.25)
        
        if db_assessment.data_sensitivity_score:
            scores.append(float(db_assessment.data_sensitivity_score))
            weights.append(0.2)
        
        if scores:
            total_weight = sum(weights)
            overall_score = sum(s * w for s, w in zip(scores, weights)) / total_weight if total_weight > 0 else 0
            db_assessment.overall_score = Decimal(str(overall_score))
            
            # 确定风险等级（使用系统配置的阈值）
            high_threshold = self.config_helper.get_risk_score_high_threshold()
            medium_threshold = self.config_helper.get_risk_score_medium_threshold()
            
            if overall_score >= high_threshold:
                db_assessment.overall_risk_level = RiskLevel.LOW
            elif overall_score >= medium_threshold:
                db_assessment.overall_risk_level = RiskLevel.MEDIUM
            elif overall_score >= 40:
                db_assessment.overall_risk_level = RiskLevel.HIGH
            else:
                db_assessment.overall_risk_level = RiskLevel.CRITICAL
        
        # 检查阈值
        self._check_thresholds(db_assessment)
        
        # 构建风险因素
        risk_factors = {
            "legal_environment": {
                "score": float(db_assessment.legal_environment_score) if db_assessment.legal_environment_score else None,
                "risk": "低" if db_assessment.legal_environment_score and db_assessment.legal_environment_score >= 70 else "中高"
            },
            "data_volume": {
                "exceeds_personal": db_assessment.exceeds_personal_threshold,
                "exceeds_sensitive": db_assessment.exceeds_sensitive_threshold
            },
            "security_measures": {
                "score": float(db_assessment.security_measures_score) if db_assessment.security_measures_score else None
            }
        }
        db_assessment.risk_factors = risk_factors
        
        # 判断是否需要监管审批
        db_assessment.requires_regulatory_approval = (
            db_assessment.exceeds_personal_threshold or
            db_assessment.exceeds_sensitive_threshold or
            db_assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        db_assessment.status = AssessmentStatus.COMPLETED
        db_assessment.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(db_assessment)
        return db_assessment
    
    def _check_thresholds(self, assessment: RiskAssessment):
        """检查阈值"""
        # 使用系统配置的阈值
        personal_threshold = self.config_helper.get_personal_info_max_threshold()
        sensitive_threshold = self.config_helper.get_sensitive_info_max_threshold()
        
        if assessment.personal_info_count:
            assessment.exceeds_personal_threshold = (
                assessment.personal_info_count >= personal_threshold
            )
        
        if assessment.sensitive_info_count:
            assessment.exceeds_sensitive_threshold = (
                assessment.sensitive_info_count >= sensitive_threshold
            )
    
    def check_thresholds(self, assessment_id: int) -> Dict[str, Any]:
        """检查阈值预警"""
        db_assessment = self.get_assessment(assessment_id)
        if not db_assessment:
            return None
        
        self._check_thresholds(db_assessment)
        self.db.commit()
        
        # 使用系统配置的阈值
        personal_threshold = self.config_helper.get_personal_info_max_threshold()
        sensitive_threshold = self.config_helper.get_sensitive_info_max_threshold()
        
        warnings = []
        if db_assessment.exceeds_personal_threshold:
            warnings.append({
                "type": "个人信息阈值",
                "message": f"个人信息数量({db_assessment.personal_info_count})超过阈值({personal_threshold})",
                "level": "high"
            })
        
        if db_assessment.exceeds_sensitive_threshold:
            warnings.append({
                "type": "敏感信息阈值",
                "message": f"敏感个人信息数量({db_assessment.sensitive_info_count})超过阈值({sensitive_threshold})",
                "level": "critical"
            })
        
        # 接近阈值预警（95%）
        if db_assessment.personal_info_count:
            threshold_95 = personal_threshold * 0.95
            if (not db_assessment.exceeds_personal_threshold and 
                db_assessment.personal_info_count >= threshold_95):
                warnings.append({
                    "type": "个人信息阈值预警",
                    "message": f"个人信息数量({db_assessment.personal_info_count})接近阈值，建议关注",
                    "level": "medium"
                })
        
        return {
            "assessment_id": assessment_id,
            "exceeds_personal_threshold": db_assessment.exceeds_personal_threshold,
            "exceeds_sensitive_threshold": db_assessment.exceeds_sensitive_threshold,
            "warnings": warnings
        }

