"""
监控仪表盘服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.audit import AuditLog, AuditAction
from app.models.scenario import CrossBorderScenario, ScenarioStatus
from app.models.risk import RiskAssessment, RiskLevel
from app.models.scenario import TransferApproval, ApprovalStatus
from app.core.config import settings


class DashboardService:
    """监控仪表盘服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_overview(self, days: int = 7) -> Dict[str, Any]:
        """获取概览统计"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 场景统计
        total_scenarios = self.db.query(CrossBorderScenario).count()
        active_scenarios = self.db.query(CrossBorderScenario).filter(
            CrossBorderScenario.status == ScenarioStatus.APPROVED
        ).count()
        
        # 审批统计
        total_approvals = self.db.query(TransferApproval).filter(
            TransferApproval.created_at >= start_date
        ).count()
        pending_approvals = self.db.query(TransferApproval).filter(
            TransferApproval.approval_status == ApprovalStatus.PENDING
        ).count()
        
        # 传输统计
        transfer_logs = self.db.query(AuditLog).filter(
            and_(
                AuditLog.action == AuditAction.TRANSFER,
                AuditLog.created_at >= start_date
            )
        ).all()
        
        total_transfers = len(transfer_logs)
        total_volume = sum(
            float(log.transfer_volume) for log in transfer_logs if log.transfer_volume
        )
        intercepted_count = len([log for log in transfer_logs if log.transfer_status == "拦截"])
        
        # 风险评估统计
        high_risk_assessments = self.db.query(RiskAssessment).filter(
            RiskAssessment.overall_risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).count()
        
        # 异常统计
        anomaly_count = self.db.query(AuditLog).filter(
            and_(
                AuditLog.is_anomaly == True,
                AuditLog.created_at >= start_date
            )
        ).count()
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "scenarios": {
                "total": total_scenarios,
                "active": active_scenarios
            },
            "approvals": {
                "total": total_approvals,
                "pending": pending_approvals
            },
            "transfers": {
                "total": total_transfers,
                "total_volume": total_volume,
                "intercepted": intercepted_count,
                "success_rate": (total_transfers - intercepted_count) / total_transfers * 100 if total_transfers > 0 else 0
            },
            "risks": {
                "high_risk_count": high_risk_assessments
            },
            "anomalies": {
                "count": anomaly_count
            }
        }
    
    def get_transfer_trends(self, days: int = 30) -> Dict[str, Any]:
        """获取传输趋势"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 按日期统计传输量
        daily_stats = (
            self.db.query(
                func.date(AuditLog.created_at).label("date"),
                func.count(AuditLog.id).label("count"),
                func.sum(AuditLog.transfer_volume).label("volume")
            )
            .filter(
                and_(
                    AuditLog.action == AuditAction.TRANSFER,
                    AuditLog.created_at >= start_date
                )
            )
            .group_by(func.date(AuditLog.created_at))
            .order_by(func.date(AuditLog.created_at))
            .all()
        )
        
        dates = []
        counts = []
        volumes = []
        
        for stat in daily_stats:
            dates.append(stat.date.isoformat())
            counts.append(stat.count)
            volumes.append(float(stat.volume) if stat.volume else 0)
        
        return {
            "dates": dates,
            "counts": counts,
            "volumes": volumes
        }
    
    def get_country_distribution(self, days: int = 30) -> Dict[str, Any]:
        """获取目的国分布"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        country_stats = (
            self.db.query(
                AuditLog.destination_country,
                func.count(AuditLog.id).label("count"),
                func.sum(AuditLog.transfer_volume).label("volume")
            )
            .filter(
                and_(
                    AuditLog.action == AuditAction.TRANSFER,
                    AuditLog.created_at >= start_date,
                    AuditLog.destination_country.isnot(None)
                )
            )
            .group_by(AuditLog.destination_country)
            .order_by(func.count(AuditLog.id).desc())
            .all()
        )
        
        countries = []
        counts = []
        volumes = []
        
        for stat in country_stats:
            countries.append(stat.destination_country)
            counts.append(stat.count)
            volumes.append(float(stat.volume) if stat.volume else 0)
        
        return {
            "countries": countries,
            "counts": counts,
            "volumes": volumes
        }
    
    def get_risk_alerts(self) -> Dict[str, Any]:
        """获取风险预警"""
        alerts = []
        
        # 检查阈值预警
        assessments = self.db.query(RiskAssessment).filter(
            RiskAssessment.exceeds_personal_threshold == True
        ).all()
        
        for assessment in assessments:
            alerts.append({
                "type": "阈值预警",
                "level": "high",
                "message": f"评估 {assessment.assessment_code} 的个人信息数量超过阈值",
                "assessment_id": assessment.id
            })
        
        # 检查高风险评估
        high_risk = self.db.query(RiskAssessment).filter(
            RiskAssessment.overall_risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).all()
        
        for assessment in high_risk:
            alerts.append({
                "type": "高风险评估",
                "level": "critical" if assessment.overall_risk_level == RiskLevel.CRITICAL else "high",
                "message": f"评估 {assessment.assessment_code} 风险等级为 {assessment.overall_risk_level}",
                "assessment_id": assessment.id
            })
        
        # 检查接近阈值（95%）
        threshold_95 = settings.PERSONAL_INFO_THRESHOLD * 0.95
        near_threshold = self.db.query(RiskAssessment).filter(
            and_(
                RiskAssessment.personal_info_count >= threshold_95,
                RiskAssessment.exceeds_personal_threshold == False
            )
        ).all()
        
        for assessment in near_threshold:
            alerts.append({
                "type": "阈值接近预警",
                "level": "medium",
                "message": f"评估 {assessment.assessment_code} 的个人信息数量接近阈值",
                "assessment_id": assessment.id
            })
        
        return {
            "alerts": alerts,
            "total": len(alerts),
            "critical": len([a for a in alerts if a["level"] == "critical"]),
            "high": len([a for a in alerts if a["level"] == "high"]),
            "medium": len([a for a in alerts if a["level"] == "medium"])
        }
    
    def get_data_asset_statistics(self) -> Dict[str, Any]:
        """获取数据资产统计"""
        from app.models.data_asset import DataAsset, DataLevel
        
        total_assets = self.db.query(DataAsset).count()
        
        # 按数据级别统计
        level_stats = (
            self.db.query(
                DataAsset.data_level,
                func.count(DataAsset.id).label("count")
            )
            .group_by(DataAsset.data_level)
            .all()
        )
        
        # 转换Enum为中文
        level_map = {
            "CORE": "核心数据",
            "IMPORTANT": "重要数据",
            "SENSITIVE": "敏感个人信息",
            "PERSONAL": "一般个人信息",
            "INTERNAL": "内部数据",
            "PUBLIC": "公开数据"
        }
        level_distribution = {
            level_map.get(str(level).split('.')[-1], str(level)): count 
            for level, count in level_stats
        }
        
        # 总记录数
        total_records = self.db.query(func.sum(DataAsset.record_count)).scalar() or 0
        
        # 总字段数
        total_fields = self.db.query(func.sum(DataAsset.field_count)).scalar() or 0
        
        return {
            "total_assets": total_assets,
            "level_distribution": level_distribution,
            "total_records": int(total_records),
            "total_fields": int(total_fields) if total_fields else 0
        }
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """获取风险评估统计"""
        total_assessments = self.db.query(RiskAssessment).count()
        
        # 按风险等级统计
        risk_level_stats = (
            self.db.query(
                RiskAssessment.overall_risk_level,
                func.count(RiskAssessment.id).label("count")
            )
            .filter(RiskAssessment.overall_risk_level.isnot(None))
            .group_by(RiskAssessment.overall_risk_level)
            .all()
        )
        
        # 转换风险等级Enum为中文
        risk_level_map = {
            "LOW": "低风险",
            "MEDIUM": "中风险",
            "HIGH": "高风险",
            "CRITICAL": "极高风险"
        }
        risk_distribution = {
            risk_level_map.get(str(level).split('.')[-1], str(level)): count 
            for level, count in risk_level_stats
        }
        
        # 按状态统计
        status_stats = (
            self.db.query(
                RiskAssessment.status,
                func.count(RiskAssessment.id).label("count")
            )
            .group_by(RiskAssessment.status)
            .all()
        )
        
        # 转换状态Enum为中文
        status_map = {
            "DRAFT": "草稿",
            "IN_PROGRESS": "进行中",
            "COMPLETED": "已完成",
            "ARCHIVED": "已归档"
        }
        status_distribution = {
            status_map.get(str(status).split('.')[-1], str(status)): count 
            for status, count in status_stats
        }
        
        # 阈值预警统计
        exceeds_personal = self.db.query(RiskAssessment).filter(
            RiskAssessment.exceeds_personal_threshold == True
        ).count()
        
        exceeds_sensitive = self.db.query(RiskAssessment).filter(
            RiskAssessment.exceeds_sensitive_threshold == True
        ).count()
        
        return {
            "total_assessments": total_assessments,
            "risk_distribution": risk_distribution,
            "status_distribution": status_distribution,
            "exceeds_personal_threshold": exceeds_personal,
            "exceeds_sensitive_threshold": exceeds_sensitive
        }
    
    def get_approval_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取审批统计"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 按状态统计
        status_stats = (
            self.db.query(
                TransferApproval.approval_status,
                func.count(TransferApproval.id).label("count")
            )
            .filter(TransferApproval.created_at >= start_date)
            .group_by(TransferApproval.approval_status)
            .all()
        )
        
        # 转换审批状态Enum为中文
        approval_status_map = {
            "PENDING": "待审批",
            "APPROVED": "已批准",
            "REJECTED": "已拒绝",
            "CANCELLED": "已取消"
        }
        status_distribution = {
            approval_status_map.get(str(status).split('.')[-1], str(status)): count 
            for status, count in status_stats
        }
        
        # 按传输类型统计
        type_stats = (
            self.db.query(
                TransferApproval.transfer_type,
                func.count(TransferApproval.id).label("count")
            )
            .filter(
                and_(
                    TransferApproval.created_at >= start_date,
                    TransferApproval.transfer_type.isnot(None)
                )
            )
            .group_by(TransferApproval.transfer_type)
            .all()
        )
        
        type_distribution = {str(transfer_type): count for transfer_type, count in type_stats}
        
        return {
            "status_distribution": status_distribution,
            "type_distribution": type_distribution
        }
    
    def get_operation_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取操作统计"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 按操作类型统计
        action_stats = (
            self.db.query(
                AuditLog.action,
                func.count(AuditLog.id).label("count")
            )
            .filter(AuditLog.created_at >= start_date)
            .group_by(AuditLog.action)
            .order_by(func.count(AuditLog.id).desc())
            .all()
        )
        
        # 转换操作类型Enum为中文
        action_map = {
            "CREATE": "创建",
            "UPDATE": "更新",
            "DELETE": "删除",
            "VIEW": "查看",
            "APPROVE": "审批",
            "REJECT": "拒绝",
            "TRANSFER": "传输",
            "INTERCEPT": "拦截",
            "EXPORT": "导出"
        }
        actions = [
            action_map.get(str(action).split('.')[-1], str(action)) 
            for action, _ in action_stats
        ]
        counts = [count for _, count in action_stats]
        
        # 按用户统计（Top 10）
        user_stats = (
            self.db.query(
                AuditLog.username,
                func.count(AuditLog.id).label("count")
            )
            .filter(
                and_(
                    AuditLog.created_at >= start_date,
                    AuditLog.username.isnot(None)
                )
            )
            .group_by(AuditLog.username)
            .order_by(func.count(AuditLog.id).desc())
            .limit(10)
            .all()
        )
        
        users = [username for username, _ in user_stats]
        user_counts = [count for _, count in user_stats]
        
        return {
            "actions": actions,
            "action_counts": counts,
            "top_users": users,
            "user_counts": user_counts
        }
    
    def get_heatmap_data(self, days: int = 30) -> Dict[str, Any]:
        """获取热力图数据（操作类型 x 日期）"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 获取所有操作类型（使用Enum）
        action_types = self.db.query(AuditLog.action).distinct().all()
        action_map = {
            "CREATE": "创建",
            "UPDATE": "更新",
            "DELETE": "删除",
            "VIEW": "查看",
            "APPROVE": "审批",
            "REJECT": "拒绝",
            "TRANSFER": "传输",
            "INTERCEPT": "拦截",
            "EXPORT": "导出"
        }
        actions = []
        action_enums = []
        for action_enum in action_types:
            action_str = str(action_enum[0]).split('.')[-1]
            actions.append(action_map.get(action_str, action_str))
            action_enums.append(action_enum[0])
        
        # 获取日期范围
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # 统计每个操作类型每天的操作次数
        heatmap_data = []
        for idx, action_enum in enumerate(action_enums):
            action_name = actions[idx]
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                count = self.db.query(func.count(AuditLog.id)).filter(
                    and_(
                        AuditLog.action == action_enum,
                        func.date(AuditLog.created_at) == date_obj.date()
                    )
                ).scalar() or 0
                if count > 0:
                    heatmap_data.append([date_str, action_name, count])
        
        return {
            "data": heatmap_data,
            "xAxis": dates,
            "yAxis": actions
        }
    
    def get_approval_funnel(self, days: int = 30) -> Dict[str, Any]:
        """获取审批流程漏斗数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        approvals = self.db.query(TransferApproval).filter(
            TransferApproval.created_at >= start_date
        ).all()
        
        total = len(approvals)
        pending = len([a for a in approvals if a.approval_status == ApprovalStatus.PENDING])
        approved = len([a for a in approvals if a.approval_status == ApprovalStatus.APPROVED])
        rejected = len([a for a in approvals if a.approval_status == ApprovalStatus.REJECTED])
        cancelled = len([a for a in approvals if a.approval_status == ApprovalStatus.CANCELLED])
        
        return {
            "data": [
                {"name": "总申请数", "value": total},
                {"name": "待审批", "value": pending},
                {"name": "已批准", "value": approved},
                {"name": "已拒绝", "value": rejected},
                {"name": "已取消", "value": cancelled}
            ]
        }
    
    def get_risk_scatter(self) -> Dict[str, Any]:
        """获取风险评估散点图数据（数据量 vs 风险等级）"""
        assessments = self.db.query(RiskAssessment).filter(
            RiskAssessment.overall_risk_level.isnot(None)
        ).all()
        
        risk_level_map = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4
        }
        
        scatter_data = []
        for assessment in assessments:
            risk_level = str(assessment.overall_risk_level).split('.')[-1]
            risk_score = risk_level_map.get(risk_level, 0)
            data_volume = assessment.personal_info_count or 0
            if data_volume > 0:
                scatter_data.append([data_volume, risk_score, assessment.id])
        
        return {
            "data": scatter_data
        }
    
    def get_risk_radar(self, assessment_id: Optional[int] = None) -> Dict[str, Any]:
        """获取风险评估雷达图数据（多维度评估）"""
        if assessment_id:
            assessments = [self.db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()]
        else:
            # 获取最近5个评估的平均值
            assessments = self.db.query(RiskAssessment).order_by(
                RiskAssessment.created_at.desc()
            ).limit(5).all()
        
        if not assessments:
            return {"data": [], "indicators": []}
        
        # 计算平均值
        avg_legal = sum(a.legal_environment_score or 0 for a in assessments) / len(assessments)
        avg_scale = sum(a.data_volume_score or 0 for a in assessments) / len(assessments)
        avg_security = sum(a.security_measures_score or 0 for a in assessments) / len(assessments)
        avg_sensitivity = sum(a.data_sensitivity_score or 0 for a in assessments) / len(assessments)
        
        indicators = [
            {"name": "法律环境", "max": 100},
            {"name": "数据规模", "max": 100},
            {"name": "安全措施", "max": 100},
            {"name": "数据敏感性", "max": 100}
        ]
        
        data = [{
            "name": "平均评估",
            "value": [avg_legal, avg_scale, avg_security, avg_sensitivity]
        }]
        
        return {
            "data": data,
            "indicators": indicators
        }

