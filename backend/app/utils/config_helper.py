"""
系统配置辅助工具
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import Any, Optional
from app.services.system_config_service import SystemConfigService


class ConfigHelper:
    """系统配置辅助类，提供便捷的配置获取方法"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_service = SystemConfigService(db)
    
    # ========== 阈值配置 ==========
    def get_personal_info_max_threshold(self) -> int:
        """获取个人信息最大数量阈值"""
        return self.config_service.get_config_value("threshold.personal_info.max", 1000000)
    
    def get_sensitive_info_max_threshold(self) -> int:
        """获取敏感个人信息最大数量阈值"""
        return self.config_service.get_config_value("threshold.sensitive_info.max", 100000)
    
    def get_risk_score_high_threshold(self) -> int:
        """获取高风险评分阈值"""
        return self.config_service.get_config_value("threshold.risk_score.high", 70)
    
    def get_risk_score_medium_threshold(self) -> int:
        """获取中风险评分阈值"""
        return self.config_service.get_config_value("threshold.risk_score.medium", 40)
    
    def get_data_volume_warning_threshold(self) -> int:
        """获取数据传输量预警阈值（GB）"""
        return self.config_service.get_config_value("threshold.data_volume.warning", 100)
    
    def get_transfer_frequency_max(self) -> int:
        """获取最大传输频率（次/天）"""
        return self.config_service.get_config_value("threshold.transfer_frequency.max", 1000)
    
    # ========== 脱敏规则 ==========
    def get_desensitization_enabled(self) -> bool:
        """获取脱敏功能开关"""
        return self.config_service.get_config_value("desensitization.enabled", True)
    
    def get_mask_middle_rule(self) -> dict:
        """获取中间脱敏规则"""
        return self.config_service.get_config_value("desensitization.mask.middle", {
            "pattern": "middle",
            "keep_start": 3,
            "keep_end": 4,
            "mask_char": "*"
        })
    
    def get_mask_email_rule(self) -> dict:
        """获取邮箱脱敏规则"""
        return self.config_service.get_config_value("desensitization.mask.email", {
            "pattern": "email",
            "mask_domain": True
        })
    
    def get_mask_id_card_rule(self) -> dict:
        """获取身份证脱敏规则"""
        return self.config_service.get_config_value("desensitization.mask.id_card", {
            "pattern": "id_card",
            "keep_start": 3,
            "keep_end": 4,
            "mask_char": "*"
        })
    
    def get_mask_bank_card_rule(self) -> dict:
        """获取银行卡脱敏规则"""
        return self.config_service.get_config_value("desensitization.mask.bank_card", {
            "pattern": "bank_card",
            "keep_end": 4,
            "mask_char": "*"
        })
    
    def get_pseudonymize_name_rule(self) -> dict:
        """获取姓名假名化规则"""
        return self.config_service.get_config_value("desensitization.pseudonymize.name", {
            "pattern": "pseudonymize",
            "algorithm": "sha256",
            "prefix": "UID_"
        })
    
    # ========== 审批流程 ==========
    def get_auto_approve_enabled(self) -> bool:
        """获取自动审批开关"""
        return self.config_service.get_config_value("approval.auto_approve.enabled", False)
    
    def get_auto_approve_risk_threshold(self) -> int:
        """获取自动审批风险阈值"""
        return self.config_service.get_config_value("approval.auto_approve.risk_threshold", 30)
    
    def get_approval_timeout_days(self) -> int:
        """获取审批超时天数"""
        return self.config_service.get_config_value("approval.timeout.days", 7)
    
    def get_require_multi_level(self) -> bool:
        """获取多级审批开关"""
        return self.config_service.get_config_value("approval.require_multi_level", True)
    
    def get_multi_level_risk_threshold(self) -> int:
        """获取多级审批风险阈值"""
        return self.config_service.get_config_value("approval.multi_level.risk_threshold", 60)
    
    # ========== 通知设置 ==========
    def get_email_notification_enabled(self) -> bool:
        """获取邮件通知开关"""
        return self.config_service.get_config_value("notification.email.enabled", True)
    
    def get_sms_notification_enabled(self) -> bool:
        """获取短信通知开关"""
        return self.config_service.get_config_value("notification.sms.enabled", False)
    
    def get_in_app_notification_enabled(self) -> bool:
        """获取站内通知开关"""
        return self.config_service.get_config_value("notification.in_app.enabled", True)
    
    def get_threshold_warning_enabled(self) -> bool:
        """获取阈值预警通知开关"""
        return self.config_service.get_config_value("notification.threshold_warning.enabled", True)
    
    def get_approval_reminder_enabled(self) -> bool:
        """获取审批提醒通知开关"""
        return self.config_service.get_config_value("notification.approval_reminder.enabled", True)
    
    def get_notification_retention_days(self) -> int:
        """获取通知保留天数"""
        return self.config_service.get_config_value("notification.retention_days", 90)
    
    # ========== 系统设置 ==========
    def get_session_timeout(self) -> int:
        """获取会话超时时间（分钟）"""
        return self.config_service.get_config_value("system.session.timeout", 30)
    
    def get_page_size(self) -> int:
        """获取默认分页大小"""
        return self.config_service.get_config_value("system.page.size", 10)
    
    def get_audit_log_retention_days(self) -> int:
        """获取审计日志保留天数"""
        return self.config_service.get_config_value("system.audit_log.retention_days", 365)
    
    def get_data_scan_interval(self) -> int:
        """获取数据扫描间隔（小时）"""
        return self.config_service.get_config_value("system.data_scan.interval", 24)
    
    def get_backup_enabled(self) -> bool:
        """获取自动备份开关"""
        return self.config_service.get_config_value("system.backup.enabled", True)
    
    def get_backup_interval(self) -> int:
        """获取备份间隔（小时）"""
        return self.config_service.get_config_value("system.backup.interval", 24)
    
    # ========== 合规规则 ==========
    def get_gdpr_enabled(self) -> bool:
        """获取GDPR合规检查开关"""
        return self.config_service.get_config_value("compliance.gdpr.enabled", True)
    
    def get_data_retention_days(self) -> int:
        """获取数据保留天数"""
        return self.config_service.get_config_value("compliance.data.retention.days", 365)
    
    def get_pipeda_enabled(self) -> bool:
        """获取PIPEDA合规检查开关"""
        return self.config_service.get_config_value("compliance.pipeda.enabled", False)
    
    def get_ccpa_enabled(self) -> bool:
        """获取CCPA合规检查开关"""
        return self.config_service.get_config_value("compliance.ccpa.enabled", False)
    
    def get_consent_required(self) -> bool:
        """获取用户同意要求"""
        return self.config_service.get_config_value("compliance.consent.required", True)
    
    def get_data_minimization(self) -> bool:
        """获取数据最小化原则开关"""
        return self.config_service.get_config_value("compliance.data.minimization", True)

