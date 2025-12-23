"""
初始化系统默认配置
作者：张彦龙
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.models.system_config import SystemConfig, ConfigCategory, ConfigType
from datetime import datetime

def init_default_configs():
    """初始化系统默认配置"""
    db = SessionLocal()
    try:
        # 获取管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("请先运行 init_users.py 创建用户")
            return
        
        print("开始创建系统默认配置...")
        
        default_configs = [
            # 阈值配置
            {
                "config_key": "threshold.personal_info.max",
                "config_name": "个人信息最大数量阈值",
                "config_value": "1000000",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.THRESHOLD,
                "description": "个人信息数量超过此阈值时触发预警",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "1000000"
            },
            {
                "config_key": "threshold.sensitive_info.max",
                "config_name": "敏感个人信息最大数量阈值",
                "config_value": "100000",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.THRESHOLD,
                "description": "敏感个人信息数量超过此阈值时触发预警",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "100000"
            },
            {
                "config_key": "threshold.risk_score.high",
                "config_name": "高风险评分阈值",
                "config_value": "70",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.THRESHOLD,
                "description": "风险评估分数超过此值视为高风险",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "70"
            },
            {
                "config_key": "threshold.risk_score.medium",
                "config_name": "中风险评分阈值",
                "config_value": "40",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.THRESHOLD,
                "description": "风险评估分数在此值到高风险阈值之间视为中风险",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "40"
            },
            {
                "config_key": "threshold.data_volume.warning",
                "config_name": "数据传输量预警阈值（GB）",
                "config_value": "100",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.THRESHOLD,
                "description": "单次数据传输量超过此值（GB）时触发预警",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "100"
            },
            {
                "config_key": "threshold.transfer_frequency.max",
                "config_name": "最大传输频率（次/天）",
                "config_value": "1000",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.THRESHOLD,
                "description": "单个场景每天最大传输次数，超过此值触发预警",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "1000"
            },
            # 脱敏规则
            {
                "config_key": "desensitization.mask.middle",
                "config_name": "中间脱敏规则",
                "config_value": '{"pattern": "middle", "keep_start": 3, "keep_end": 4, "mask_char": "*"}',
                "config_type": ConfigType.JSON,
                "category": ConfigCategory.DESENSITIZATION,
                "description": "手机号、身份证等中间部分脱敏规则",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": '{"pattern": "middle", "keep_start": 3, "keep_end": 4, "mask_char": "*"}'
            },
            {
                "config_key": "desensitization.mask.email",
                "config_name": "邮箱脱敏规则",
                "config_value": '{"pattern": "email", "mask_domain": true}',
                "config_type": ConfigType.JSON,
                "category": ConfigCategory.DESENSITIZATION,
                "description": "邮箱地址脱敏规则",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": '{"pattern": "email", "mask_domain": true}'
            },
            {
                "config_key": "desensitization.mask.id_card",
                "config_name": "身份证脱敏规则",
                "config_value": '{"pattern": "id_card", "keep_start": 3, "keep_end": 4, "mask_char": "*"}',
                "config_type": ConfigType.JSON,
                "category": ConfigCategory.DESENSITIZATION,
                "description": "身份证号码脱敏规则，保留前3位和后4位",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": '{"pattern": "id_card", "keep_start": 3, "keep_end": 4, "mask_char": "*"}'
            },
            {
                "config_key": "desensitization.mask.bank_card",
                "config_name": "银行卡脱敏规则",
                "config_value": '{"pattern": "bank_card", "keep_end": 4, "mask_char": "*"}',
                "config_type": ConfigType.JSON,
                "category": ConfigCategory.DESENSITIZATION,
                "description": "银行卡号脱敏规则，只保留后4位",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": '{"pattern": "bank_card", "keep_end": 4, "mask_char": "*"}'
            },
            {
                "config_key": "desensitization.pseudonymize.name",
                "config_name": "姓名假名化规则",
                "config_value": '{"pattern": "pseudonymize", "algorithm": "sha256", "prefix": "UID_"}',
                "config_type": ConfigType.JSON,
                "category": ConfigCategory.DESENSITIZATION,
                "description": "姓名假名化规则，使用SHA256哈希生成唯一标识",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": '{"pattern": "pseudonymize", "algorithm": "sha256", "prefix": "UID_"}'
            },
            {
                "config_key": "desensitization.enabled",
                "config_name": "脱敏功能开关",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.DESENSITIZATION,
                "description": "是否启用数据脱敏功能",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            # 审批流程
            {
                "config_key": "approval.auto_approve.enabled",
                "config_name": "自动审批开关",
                "config_value": "false",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.APPROVAL,
                "description": "是否启用自动审批（低风险场景）",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "false"
            },
            {
                "config_key": "approval.auto_approve.risk_threshold",
                "config_name": "自动审批风险阈值",
                "config_value": "30",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.APPROVAL,
                "description": "风险评分低于此值可自动审批",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "30"
            },
            {
                "config_key": "approval.timeout.days",
                "config_name": "审批超时天数",
                "config_value": "7",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.APPROVAL,
                "description": "审批申请超过此天数未处理则自动拒绝",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "7"
            },
            {
                "config_key": "approval.require_multi_level",
                "config_name": "多级审批开关",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.APPROVAL,
                "description": "高风险场景是否需要多级审批",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "approval.multi_level.risk_threshold",
                "config_name": "多级审批风险阈值",
                "config_value": "60",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.APPROVAL,
                "description": "风险评分超过此值需要多级审批",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "60"
            },
            # 通知设置
            {
                "config_key": "notification.email.enabled",
                "config_name": "邮件通知开关",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.NOTIFICATION,
                "description": "是否启用邮件通知",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "notification.sms.enabled",
                "config_name": "短信通知开关",
                "config_value": "false",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.NOTIFICATION,
                "description": "是否启用短信通知",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "false"
            },
            {
                "config_key": "notification.in_app.enabled",
                "config_name": "站内通知开关",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.NOTIFICATION,
                "description": "是否启用站内通知",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "notification.threshold_warning.enabled",
                "config_name": "阈值预警通知开关",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.NOTIFICATION,
                "description": "是否启用阈值预警通知",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "notification.approval_reminder.enabled",
                "config_name": "审批提醒通知开关",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.NOTIFICATION,
                "description": "是否启用审批提醒通知",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "notification.retention_days",
                "config_name": "通知保留天数",
                "config_value": "90",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.NOTIFICATION,
                "description": "通知消息保留天数，超过此天数自动删除",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "90"
            },
            # 系统设置
            {
                "config_key": "system.session.timeout",
                "config_name": "会话超时时间（分钟）",
                "config_value": "30",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.SYSTEM,
                "description": "用户会话超时时间（分钟）",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": True,
                "default_value": "30"
            },
            {
                "config_key": "system.page.size",
                "config_name": "默认分页大小",
                "config_value": "10",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.SYSTEM,
                "description": "列表页面默认每页显示数量",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": True,
                "default_value": "10"
            },
            {
                "config_key": "system.audit_log.retention_days",
                "config_name": "审计日志保留天数",
                "config_value": "365",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.SYSTEM,
                "description": "审计日志保留天数，超过此天数自动归档或删除",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "365"
            },
            {
                "config_key": "system.data_scan.interval",
                "config_name": "数据扫描间隔（小时）",
                "config_value": "24",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.SYSTEM,
                "description": "自动数据资产扫描间隔（小时）",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "24"
            },
            {
                "config_key": "system.backup.enabled",
                "config_name": "自动备份开关",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.SYSTEM,
                "description": "是否启用自动备份",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "system.backup.interval",
                "config_name": "备份间隔（小时）",
                "config_value": "24",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.SYSTEM,
                "description": "自动备份间隔（小时）",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "24"
            },
            # 合规规则
            {
                "config_key": "compliance.gdpr.enabled",
                "config_name": "GDPR合规检查",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.COMPLIANCE,
                "description": "是否启用GDPR合规检查",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "compliance.data.retention.days",
                "config_name": "数据保留天数",
                "config_value": "365",
                "config_type": ConfigType.INTEGER,
                "category": ConfigCategory.COMPLIANCE,
                "description": "数据保留天数，超过此天数自动删除",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "365"
            },
            {
                "config_key": "compliance.pipeda.enabled",
                "config_name": "PIPEDA合规检查",
                "config_value": "false",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.COMPLIANCE,
                "description": "是否启用PIPEDA（加拿大个人信息保护）合规检查",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "false"
            },
            {
                "config_key": "compliance.ccpa.enabled",
                "config_name": "CCPA合规检查",
                "config_value": "false",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.COMPLIANCE,
                "description": "是否启用CCPA（加州消费者隐私法）合规检查",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "false"
            },
            {
                "config_key": "compliance.consent.required",
                "config_name": "用户同意要求",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.COMPLIANCE,
                "description": "跨境传输是否需要用户明确同意",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            },
            {
                "config_key": "compliance.data.minimization",
                "config_name": "数据最小化原则",
                "config_value": "true",
                "config_type": ConfigType.BOOLEAN,
                "category": ConfigCategory.COMPLIANCE,
                "description": "是否启用数据最小化原则（只传输必要数据）",
                "is_encrypted": False,
                "is_editable": True,
                "is_public": False,
                "default_value": "true"
            }
        ]
        
        created_count = 0
        for config_data in default_configs:
            # 检查是否已存在
            existing = db.query(SystemConfig).filter(
                SystemConfig.config_key == config_data["config_key"]
            ).first()
            
            if not existing:
                config = SystemConfig(
                    **config_data,
                    updated_by=admin.id,
                    created_at=datetime.now()
                )
                db.add(config)
                created_count += 1
        
        db.commit()
        print(f"✅ 已创建 {created_count} 个系统默认配置")
        print(f"   - 阈值配置: {len([c for c in default_configs if c['category'] == ConfigCategory.THRESHOLD])} 个")
        print(f"   - 脱敏规则: {len([c for c in default_configs if c['category'] == ConfigCategory.DESENSITIZATION])} 个")
        print(f"   - 审批流程: {len([c for c in default_configs if c['category'] == ConfigCategory.APPROVAL])} 个")
        print(f"   - 通知设置: {len([c for c in default_configs if c['category'] == ConfigCategory.NOTIFICATION])} 个")
        print(f"   - 系统设置: {len([c for c in default_configs if c['category'] == ConfigCategory.SYSTEM])} 个")
        print(f"   - 合规规则: {len([c for c in default_configs if c['category'] == ConfigCategory.COMPLIANCE])} 个")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_default_configs()

