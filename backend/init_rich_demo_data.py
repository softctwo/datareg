"""
初始化丰富的演示数据 - 覆盖所有业务场景和类型
作者：张彦龙
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.models.data_asset import DataAsset, DataClassification, SensitiveTag, DataLevel
from app.models.scenario import CrossBorderScenario, ScenarioStatus, TransferApproval, ApprovalStatus
from app.models.risk import RiskAssessment, RiskLevel, AssessmentStatus
from app.models.audit import AuditLog, AuditAction
from datetime import datetime, timedelta
from decimal import Decimal
import json
import random

def init_rich_demo_data():
    """初始化丰富的演示数据"""
    db = SessionLocal()
    try:
        # 获取管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("请先运行 init_users.py 创建用户")
            return
        
        print("=" * 60)
        print("开始创建丰富的演示数据...")
        print("=" * 60)
        
        # 1. 创建数据分类
        print("\n[1/7] 创建数据分类...")
        classifications = [
            DataClassification(category_name="客户信息", category_code="CUST_INFO", level=1, description="客户相关数据"),
            DataClassification(category_name="交易数据", category_code="TRAN_DATA", level=1, description="交易相关数据"),
            DataClassification(category_name="风险数据", category_code="RISK_DATA", level=1, description="风险相关数据"),
            DataClassification(category_name="财务数据", category_code="FIN_DATA", level=1, description="财务相关数据"),
            DataClassification(category_name="产品数据", category_code="PROD_DATA", level=1, description="产品相关数据"),
            DataClassification(category_name="运营数据", category_code="OPS_DATA", level=1, description="运营相关数据"),
        ]
        for cls in classifications:
            existing = db.query(DataClassification).filter(
                DataClassification.category_code == cls.category_code
            ).first()
            if not existing:
                db.add(cls)
        db.commit()
        print(f"✅ 已创建/更新 {len(classifications)} 个数据分类")
        
        # 获取分类ID
        classifications_dict = {}
        for cls_code in ["CUST_INFO", "TRAN_DATA", "RISK_DATA", "FIN_DATA", "PROD_DATA", "OPS_DATA"]:
            cls = db.query(DataClassification).filter(DataClassification.category_code == cls_code).first()
            if cls:
                classifications_dict[cls_code] = cls.id
        
        # 2. 创建敏感标签
        print("\n[2/7] 创建敏感标签...")
        tags = [
            SensitiveTag(tag_name="身份证号", tag_code="ID_CARD", tag_type="PII", detection_rule="ID_NO|IDNO|身份证", risk_level="高", description="身份证号码标识"),
            SensitiveTag(tag_name="手机号", tag_code="MOBILE", tag_type="PII", detection_rule="MOB_NO|MOBILE|手机", risk_level="高", description="手机号码标识"),
            SensitiveTag(tag_name="银行卡号", tag_code="BANK_CARD", tag_type="PII", detection_rule="CARD_NO|ACCT_NO|银行卡", risk_level="高", description="银行卡号标识"),
            SensitiveTag(tag_name="邮箱", tag_code="EMAIL", tag_type="PII", detection_rule="EMAIL|邮箱", risk_level="中", description="邮箱地址标识"),
            SensitiveTag(tag_name="姓名", tag_code="NAME", tag_type="PII", detection_rule="CUST_NM|NAME|姓名", risk_level="中", description="客户姓名标识"),
            SensitiveTag(tag_name="信贷总量", tag_code="CREDIT_TOTAL", tag_type="重要数据", detection_rule="信贷总量|CREDIT_TOTAL", risk_level="中", description="信贷总量数据"),
            SensitiveTag(tag_name="账户余额", tag_code="ACCT_BAL", tag_type="重要数据", detection_rule="ACCT_BAL|账户余额", risk_level="中", description="账户余额数据"),
            SensitiveTag(tag_name="交易金额", tag_code="TRAN_AMT", tag_type="重要数据", detection_rule="TRAN_AMT|交易金额", risk_level="低", description="交易金额数据"),
        ]
        for tag in tags:
            existing = db.query(SensitiveTag).filter(SensitiveTag.tag_code == tag.tag_code).first()
            if not existing:
                db.add(tag)
        db.commit()
        print(f"✅ 已创建/更新 {len(tags)} 个敏感标签")
        
        # 3. 创建丰富的数据资产（覆盖所有类型、级别、状态）
        print("\n[3/7] 创建丰富的数据资产...")
        asset_types = ["表", "视图", "接口", "文件"]
        data_levels = [DataLevel.CORE, DataLevel.IMPORTANT, DataLevel.SENSITIVE, DataLevel.PERSONAL, DataLevel.INTERNAL, DataLevel.PUBLIC]
        source_systems = ["数据仓库", "核心系统", "风险系统", "财务系统", "CRM系统", "风控系统", "运营系统"]
        
        assets_data = [
            # 表类型 - 核心数据
            {"name": "DWS_CUST_ALL", "code": "DWS_CUST_ALL", "type": "表", "level": DataLevel.CORE, "class": "CUST_INFO", "system": "数据仓库", "schema": "dws", "table": "cust_all", "fields": 25, "records": 1000000, "desc": "全量客户信息表，包含客户基本信息和联系方式", "active": True},
            {"name": "CORE_ACCT_MASTER", "code": "CORE_ACCT_MASTER", "type": "表", "level": DataLevel.CORE, "class": "TRAN_DATA", "system": "核心系统", "schema": "core", "table": "acct_master", "fields": 30, "records": 2000000, "desc": "账户主表，包含账户基本信息", "active": True},
            
            # 表类型 - 重要数据
            {"name": "DWS_FINA_GL", "code": "DWS_FINA_GL", "type": "表", "level": DataLevel.IMPORTANT, "class": "FIN_DATA", "system": "数据仓库", "schema": "dws", "table": "fina_gl", "fields": 30, "records": 500000, "desc": "总账表，包含财务科目和余额信息", "active": True},
            {"name": "RISK_EXPOSURE_SUMMARY", "code": "RISK_EXPOSURE_SUMMARY", "type": "表", "level": DataLevel.IMPORTANT, "class": "RISK_DATA", "system": "风险系统", "schema": "risk", "table": "exposure_summary", "fields": 15, "records": 100000, "desc": "风险暴露汇总表", "active": True},
            {"name": "DWS_TRAN_ACCT_INNER_TX", "code": "DWS_TRAN_ACCT_INNER_TX", "type": "表", "level": DataLevel.IMPORTANT, "class": "TRAN_DATA", "system": "数据仓库", "schema": "dws", "table": "tran_acct_inner_tx", "fields": 20, "records": 5000000, "desc": "内部账户交易明细表", "active": True},
            
            # 表类型 - 敏感个人信息
            {"name": "CUST_PERSONAL_INFO", "code": "CUST_PERSONAL_INFO", "type": "表", "level": DataLevel.SENSITIVE, "class": "CUST_INFO", "system": "CRM系统", "schema": "crm", "table": "cust_personal_info", "fields": 18, "records": 800000, "desc": "客户个人信息表，包含身份证、手机号等敏感信息", "active": True},
            {"name": "CUST_BANK_CARD_INFO", "code": "CUST_BANK_CARD_INFO", "type": "表", "level": DataLevel.SENSITIVE, "class": "CUST_INFO", "system": "核心系统", "schema": "core", "table": "cust_bank_card_info", "fields": 12, "records": 1500000, "desc": "客户银行卡信息表", "active": True},
            
            # 表类型 - 个人信息
            {"name": "CUST_BASIC_INFO", "code": "CUST_BASIC_INFO", "type": "表", "level": DataLevel.PERSONAL, "class": "CUST_INFO", "system": "CRM系统", "schema": "crm", "table": "cust_basic_info", "fields": 15, "records": 2000000, "desc": "客户基本信息表", "active": True},
            {"name": "PROD_SALES_RECORD", "code": "PROD_SALES_RECORD", "type": "表", "level": DataLevel.PERSONAL, "class": "PROD_DATA", "system": "运营系统", "schema": "ops", "table": "prod_sales_record", "fields": 10, "records": 3000000, "desc": "产品销售记录表", "active": True},
            
            # 表类型 - 内部数据
            {"name": "OPS_SYSTEM_LOG", "code": "OPS_SYSTEM_LOG", "type": "表", "level": DataLevel.INTERNAL, "class": "OPS_DATA", "system": "运营系统", "schema": "ops", "table": "system_log", "fields": 8, "records": 10000000, "desc": "系统操作日志表", "active": True},
            {"name": "RISK_RULE_CONFIG", "code": "RISK_RULE_CONFIG", "type": "表", "level": DataLevel.INTERNAL, "class": "RISK_DATA", "system": "风控系统", "schema": "risk", "table": "rule_config", "fields": 12, "records": 5000, "desc": "风控规则配置表", "active": True},
            
            # 表类型 - 公开数据
            {"name": "PUBLIC_EXCHANGE_RATE", "code": "PUBLIC_EXCHANGE_RATE", "type": "表", "level": DataLevel.PUBLIC, "class": "FIN_DATA", "system": "财务系统", "schema": "fin", "table": "exchange_rate", "fields": 5, "records": 10000, "desc": "公开汇率表", "active": True},
            
            # 视图类型
            {"name": "VW_CUST_SUMMARY", "code": "VW_CUST_SUMMARY", "type": "视图", "level": DataLevel.IMPORTANT, "class": "CUST_INFO", "system": "数据仓库", "schema": "dws", "table": "vw_cust_summary", "fields": 20, "records": 1000000, "desc": "客户汇总视图", "active": True},
            {"name": "VW_TRAN_DAILY", "code": "VW_TRAN_DAILY", "type": "视图", "level": DataLevel.IMPORTANT, "class": "TRAN_DATA", "system": "数据仓库", "schema": "dws", "table": "vw_tran_daily", "fields": 15, "records": 5000000, "desc": "每日交易汇总视图", "active": True},
            {"name": "VW_RISK_METRICS", "code": "VW_RISK_METRICS", "type": "视图", "level": DataLevel.INTERNAL, "class": "RISK_DATA", "system": "风险系统", "schema": "risk", "table": "vw_risk_metrics", "fields": 10, "records": 100000, "desc": "风险指标视图", "active": True},
            {"name": "VW_FIN_MONTHLY", "code": "VW_FIN_MONTHLY", "type": "视图", "level": DataLevel.INTERNAL, "class": "FIN_DATA", "system": "财务系统", "schema": "fin", "table": "vw_fin_monthly", "fields": 12, "records": 50000, "desc": "月度财务汇总视图", "active": False},
            
            # 接口类型
            {"name": "API_CUST_QUERY", "code": "API_CUST_QUERY", "type": "接口", "level": DataLevel.SENSITIVE, "class": "CUST_INFO", "system": "CRM系统", "schema": None, "table": None, "fields": None, "records": None, "desc": "客户信息查询接口", "active": True},
            {"name": "API_TRAN_SUBMIT", "code": "API_TRAN_SUBMIT", "type": "接口", "level": DataLevel.IMPORTANT, "class": "TRAN_DATA", "system": "核心系统", "schema": None, "table": None, "fields": None, "records": None, "desc": "交易提交接口", "active": True},
            {"name": "API_RISK_CHECK", "code": "API_RISK_CHECK", "type": "接口", "level": DataLevel.INTERNAL, "class": "RISK_DATA", "system": "风控系统", "schema": None, "table": None, "fields": None, "records": None, "desc": "风险检查接口", "active": True},
            {"name": "API_FIN_REPORT", "code": "API_FIN_REPORT", "type": "接口", "level": DataLevel.INTERNAL, "class": "FIN_DATA", "system": "财务系统", "schema": None, "table": None, "fields": None, "records": None, "desc": "财务报表接口", "active": False},
            
            # 文件类型
            {"name": "FILE_CUST_EXPORT", "code": "FILE_CUST_EXPORT", "type": "文件", "level": DataLevel.SENSITIVE, "class": "CUST_INFO", "system": "数据仓库", "schema": None, "table": None, "fields": None, "records": None, "desc": "客户信息导出文件", "active": True},
            {"name": "FILE_TRAN_BATCH", "code": "FILE_TRAN_BATCH", "type": "文件", "level": DataLevel.IMPORTANT, "class": "TRAN_DATA", "system": "核心系统", "schema": None, "table": None, "fields": None, "records": None, "desc": "批量交易文件", "active": True},
            {"name": "FILE_RISK_REPORT", "code": "FILE_RISK_REPORT", "type": "文件", "level": DataLevel.INTERNAL, "class": "RISK_DATA", "system": "风险系统", "schema": None, "table": None, "fields": None, "records": None, "desc": "风险报告文件", "active": True},
            {"name": "FILE_FIN_STATEMENT", "code": "FILE_FIN_STATEMENT", "type": "文件", "level": DataLevel.INTERNAL, "class": "FIN_DATA", "system": "财务系统", "schema": None, "table": None, "fields": None, "records": None, "desc": "财务报表文件", "active": False},
        ]
        
        assets = []
        for asset_data in assets_data:
            existing = db.query(DataAsset).filter(DataAsset.asset_code == asset_data["code"]).first()
            if existing:
                # 更新现有资产
                existing.asset_type = asset_data["type"]
                existing.data_level = asset_data["level"]
                existing.classification_id = classifications_dict.get(asset_data["class"])
                existing.field_count = asset_data["fields"]
                existing.record_count = asset_data["records"]
                existing.description = asset_data["desc"]
                existing.is_active = asset_data["active"]
                existing.last_scan_time = datetime.now() - timedelta(days=random.randint(1, 30))
                assets.append(existing)
            else:
                # 创建新资产
                asset = DataAsset(
                    asset_name=asset_data["name"],
                    asset_code=asset_data["code"],
                    asset_type=asset_data["type"],
                    source_system=asset_data["system"],
                    schema_name=asset_data["schema"],
                    table_name=asset_data["table"],
                    data_level=asset_data["level"],
                    classification_id=classifications_dict.get(asset_data["class"]),
                    field_count=asset_data["fields"],
                    record_count=asset_data["records"],
                    description=asset_data["desc"],
                    is_active=asset_data["active"],
                    last_scan_time=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.add(asset)
                assets.append(asset)
        db.commit()
        print(f"✅ 已创建 {len(assets)} 个数据资产")
        print(f"   - 表: {len([a for a in assets if a.asset_type == '表'])} 个")
        print(f"   - 视图: {len([a for a in assets if a.asset_type == '视图'])} 个")
        print(f"   - 接口: {len([a for a in assets if a.asset_type == '接口'])} 个")
        print(f"   - 文件: {len([a for a in assets if a.asset_type == '文件'])} 个")
        print(f"   - 启用: {len([a for a in assets if a.is_active])} 个")
        print(f"   - 禁用: {len([a for a in assets if not a.is_active])} 个")
        
        # 获取所有资产ID用于后续关联
        all_assets = db.query(DataAsset).all()
        asset_ids = [a.id for a in all_assets]
        
        # 4. 创建丰富的跨境场景（覆盖所有状态、业务类型、传输频率）
        print("\n[4/7] 创建丰富的跨境场景...")
        scenario_statuses = [ScenarioStatus.DRAFT, ScenarioStatus.PENDING, ScenarioStatus.APPROVED, ScenarioStatus.REJECTED, ScenarioStatus.EXPIRED, ScenarioStatus.SUSPENDED]
        business_types = ["审计", "合规审查", "报表汇总", "业务分析", "系统对接", "数据备份"]
        transfer_frequencies = ["实时", "日", "周", "月", "一次性"]
        recipient_countries = ["美国", "新加坡", "香港", "日本", "英国", "德国", "澳大利亚"]
        
        scenarios_data = [
            {"name": "母行集团年度审计", "code": "SCEN_001", "business": "审计", "status": ScenarioStatus.APPROVED, "country": "美国", "type": "母行", "freq": "一次性", "volume": 500000, "days": 30},
            {"name": "跨境贸易融资合规审查", "code": "SCEN_002", "business": "合规审查", "status": ScenarioStatus.PENDING, "country": "新加坡", "type": "境外分行", "freq": "月", "volume": 200000, "days": 0},
            {"name": "境外分行报表汇总", "code": "SCEN_003", "business": "报表汇总", "status": ScenarioStatus.DRAFT, "country": "香港", "type": "境外分行", "freq": "月", "volume": 100000, "days": 0},
            {"name": "亚太区业务分析", "code": "SCEN_004", "business": "业务分析", "status": ScenarioStatus.APPROVED, "country": "新加坡", "type": "境外分行", "freq": "周", "volume": 150000, "days": 15},
            {"name": "系统对接数据同步", "code": "SCEN_005", "business": "系统对接", "status": ScenarioStatus.APPROVED, "country": "日本", "type": "第三方机构", "freq": "实时", "volume": 300000, "days": 7},
            {"name": "数据备份存储", "code": "SCEN_006", "business": "数据备份", "status": ScenarioStatus.REJECTED, "country": "美国", "type": "第三方机构", "freq": "日", "volume": 1000000, "days": 0},
            {"name": "季度财务审计", "code": "SCEN_007", "business": "审计", "status": ScenarioStatus.EXPIRED, "country": "英国", "type": "母行", "freq": "一次性", "volume": 400000, "days": -90},
            {"name": "风险数据共享", "code": "SCEN_008", "business": "业务分析", "status": ScenarioStatus.SUSPENDED, "country": "德国", "type": "第三方机构", "freq": "月", "volume": 250000, "days": -10},
            {"name": "客户服务数据同步", "code": "SCEN_009", "business": "系统对接", "status": ScenarioStatus.PENDING, "country": "澳大利亚", "type": "境外分行", "freq": "实时", "volume": 180000, "days": 0},
            {"name": "监管报告提交", "code": "SCEN_010", "business": "合规审查", "status": ScenarioStatus.APPROVED, "country": "香港", "type": "境外分行", "freq": "月", "volume": 120000, "days": 5},
        ]
        
        scenarios = []
        for scen_data in scenarios_data:
            existing = db.query(CrossBorderScenario).filter(CrossBorderScenario.scenario_code == scen_data["code"]).first()
            if existing:
                # 更新现有场景
                existing.business_type = scen_data["business"]
                existing.status = scen_data["status"]
                existing.transfer_frequency = scen_data["freq"]
                existing.estimated_volume = Decimal(str(scen_data["volume"]))
                if scen_data["status"] == ScenarioStatus.APPROVED and scen_data["days"] > 0:
                    existing.approver_id = admin.id
                    existing.approved_at = datetime.now() - timedelta(days=scen_data["days"])
                    existing.expiry_date = datetime.now() + timedelta(days=365 - scen_data["days"])
                elif scen_data["status"] == ScenarioStatus.EXPIRED:
                    existing.approver_id = admin.id
                    existing.approved_at = datetime.now() - timedelta(days=abs(scen_data["days"]) + 365)
                    existing.expiry_date = datetime.now() - timedelta(days=abs(scen_data["days"]))
                scenarios.append(existing)
            else:
                # 创建新场景
                scenario = CrossBorderScenario(
                    scenario_name=scen_data["name"],
                    scenario_code=scen_data["code"],
                    business_type=scen_data["business"],
                    recipient_name=f"{scen_data['country']}接收方",
                    recipient_country=scen_data["country"],
                    recipient_type=scen_data["type"],
                    data_purpose=f"{scen_data['business']}相关数据用途",
                    storage_duration=365 if scen_data["freq"] == "一次性" else 180,
                    transfer_frequency=scen_data["freq"],
                    security_level="高" if scen_data["status"] == ScenarioStatus.APPROVED else "中",
                    encryption_method="AES-256" if scen_data["status"] == ScenarioStatus.APPROVED else "AES-128",
                    data_scope=f"{scen_data['business']}相关数据范围",
                    estimated_volume=Decimal(str(scen_data["volume"])),
                    status=scen_data["status"],
                    created_by=admin.id,
                )
                if scen_data["status"] == ScenarioStatus.APPROVED and scen_data["days"] > 0:
                    scenario.approver_id = admin.id
                    scenario.approved_at = datetime.now() - timedelta(days=scen_data["days"])
                    scenario.expiry_date = datetime.now() + timedelta(days=365 - scen_data["days"])
                elif scen_data["status"] == ScenarioStatus.EXPIRED:
                    scenario.approver_id = admin.id
                    scenario.approved_at = datetime.now() - timedelta(days=abs(scen_data["days"]) + 365)
                    scenario.expiry_date = datetime.now() - timedelta(days=abs(scen_data["days"]))
                db.add(scenario)
                scenarios.append(scenario)
        db.commit()
        print(f"✅ 已创建 {len(scenarios)} 个跨境场景")
        print(f"   - 草稿: {len([s for s in scenarios if s.status == ScenarioStatus.DRAFT])} 个")
        print(f"   - 待审批: {len([s for s in scenarios if s.status == ScenarioStatus.PENDING])} 个")
        print(f"   - 已批准: {len([s for s in scenarios if s.status == ScenarioStatus.APPROVED])} 个")
        print(f"   - 已拒绝: {len([s for s in scenarios if s.status == ScenarioStatus.REJECTED])} 个")
        print(f"   - 已过期: {len([s for s in scenarios if s.status == ScenarioStatus.EXPIRED])} 个")
        print(f"   - 已暂停: {len([s for s in scenarios if s.status == ScenarioStatus.SUSPENDED])} 个")
        
        # 获取场景ID
        scenarios_dict = {}
        for scen_code in [f"SCEN_{i:03d}" for i in range(1, 11)]:
            scen = db.query(CrossBorderScenario).filter(CrossBorderScenario.scenario_code == scen_code).first()
            if scen:
                scenarios_dict[scen_code] = scen.id
        
        # 5. 创建丰富的风险评估（覆盖PIA/DPIA，所有状态和风险级别）
        print("\n[5/7] 创建丰富的风险评估...")
        assessment_types = ["PIA", "DPIA"]
        assessment_statuses = [AssessmentStatus.DRAFT, AssessmentStatus.IN_PROGRESS, AssessmentStatus.COMPLETED, AssessmentStatus.ARCHIVED]
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        assessments_data = [
            {"name": "母行审计风险评估", "code": "RISK_001", "type": "PIA", "status": AssessmentStatus.COMPLETED, "level": RiskLevel.MEDIUM, "scen": "SCEN_001", "scores": [75, 60, 85, 70], "overall": 72.5, "personal": 500000, "sensitive": 100000},
            {"name": "跨境贸易融资风险评估", "code": "RISK_002", "type": "DPIA", "status": AssessmentStatus.COMPLETED, "level": RiskLevel.LOW, "scen": "SCEN_002", "scores": [80, 50, 70, 65], "overall": 66.25, "personal": 200000, "sensitive": 50000},
            {"name": "报表汇总风险评估", "code": "RISK_003", "type": "PIA", "status": AssessmentStatus.IN_PROGRESS, "level": RiskLevel.LOW, "scen": "SCEN_003", "scores": [70, 40, 75, 60], "overall": 61.25, "personal": 100000, "sensitive": 20000},
            {"name": "业务分析风险评估", "code": "RISK_004", "type": "DPIA", "status": AssessmentStatus.COMPLETED, "level": RiskLevel.MEDIUM, "scen": "SCEN_004", "scores": [65, 55, 80, 75], "overall": 68.75, "personal": 150000, "sensitive": 80000},
            {"name": "系统对接风险评估", "code": "RISK_005", "type": "PIA", "status": AssessmentStatus.COMPLETED, "level": RiskLevel.HIGH, "scen": "SCEN_005", "scores": [60, 80, 60, 85], "overall": 71.25, "personal": 300000, "sensitive": 150000},
            {"name": "数据备份风险评估", "code": "RISK_006", "type": "DPIA", "status": AssessmentStatus.ARCHIVED, "level": RiskLevel.CRITICAL, "scen": "SCEN_006", "scores": [50, 95, 50, 90], "overall": 71.25, "personal": 1000000, "sensitive": 500000},
            {"name": "季度审计风险评估", "code": "RISK_007", "type": "PIA", "status": AssessmentStatus.ARCHIVED, "level": RiskLevel.MEDIUM, "scen": "SCEN_007", "scores": [70, 55, 75, 70], "overall": 67.5, "personal": 400000, "sensitive": 100000},
            {"name": "风险数据共享评估", "code": "RISK_008", "type": "DPIA", "status": AssessmentStatus.DRAFT, "level": RiskLevel.MEDIUM, "scen": "SCEN_008", "scores": [65, 60, 70, 75], "overall": 67.5, "personal": 250000, "sensitive": 120000},
            {"name": "客户服务数据评估", "code": "RISK_009", "type": "PIA", "status": AssessmentStatus.IN_PROGRESS, "level": RiskLevel.LOW, "scen": "SCEN_009", "scores": [75, 45, 80, 65], "overall": 66.25, "personal": 180000, "sensitive": 40000},
            {"name": "监管报告评估", "code": "RISK_010", "type": "PIA", "status": AssessmentStatus.COMPLETED, "level": RiskLevel.LOW, "scen": "SCEN_010", "scores": [80, 40, 85, 60], "overall": 66.25, "personal": 120000, "sensitive": 30000},
        ]
        
        assessments = []
        for assess_data in assessments_data:
            existing = db.query(RiskAssessment).filter(RiskAssessment.assessment_code == assess_data["code"]).first()
            if existing:
                # 更新现有评估
                existing.assessment_type = assess_data["type"]
                existing.legal_environment_score = Decimal(str(assess_data["scores"][0]))
                existing.data_volume_score = Decimal(str(assess_data["scores"][1]))
                existing.security_measures_score = Decimal(str(assess_data["scores"][2]))
                existing.data_sensitivity_score = Decimal(str(assess_data["scores"][3]))
                existing.personal_info_count = Decimal(str(assess_data["personal"]))
                existing.sensitive_info_count = Decimal(str(assess_data["sensitive"]))
                existing.exceeds_personal_threshold = assess_data["personal"] >= 1000000
                existing.exceeds_sensitive_threshold = assess_data["sensitive"] >= 100000
                existing.overall_risk_level = assess_data["level"]
                existing.overall_score = Decimal(str(assess_data["overall"]))
                existing.status = assess_data["status"]
                if assess_data["status"] == AssessmentStatus.COMPLETED:
                    existing.completed_at = datetime.now() - timedelta(days=random.randint(1, 30))
                elif assess_data["status"] == AssessmentStatus.ARCHIVED:
                    existing.completed_at = datetime.now() - timedelta(days=random.randint(60, 180))
                    existing.reviewed_by = admin.id
                assessments.append(existing)
            else:
                # 创建新评估
                assessment = RiskAssessment(
                    assessment_name=assess_data["name"],
                    assessment_code=assess_data["code"],
                    assessment_type=assess_data["type"],
                    scenario_id=scenarios_dict.get(assess_data["scen"], 1),
                    legal_environment_score=Decimal(str(assess_data["scores"][0])),
                    data_volume_score=Decimal(str(assess_data["scores"][1])),
                    security_measures_score=Decimal(str(assess_data["scores"][2])),
                    data_sensitivity_score=Decimal(str(assess_data["scores"][3])),
                    personal_info_count=Decimal(str(assess_data["personal"])),
                    sensitive_info_count=Decimal(str(assess_data["sensitive"])),
                    exceeds_personal_threshold=assess_data["personal"] >= 1000000,
                    exceeds_sensitive_threshold=assess_data["sensitive"] >= 100000,
                    overall_risk_level=assess_data["level"],
                    overall_score=Decimal(str(assess_data["overall"])),
                    risk_factors={"legal": assess_data["scores"][0], "volume": assess_data["scores"][1], "security": assess_data["scores"][2], "sensitivity": assess_data["scores"][3]},
                    mitigation_measures="使用加密传输，实施数据脱敏，签署标准合同",
                    assessment_result=f"{assess_data['level'].value}，建议加强数据保护措施",
                    requires_regulatory_approval=assess_data["level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL],
                    recommendation="建议进行数据脱敏处理，并签署数据出境标准合同",
                    status=assess_data["status"],
                    assessor_id=admin.id,
                )
                if assess_data["status"] == AssessmentStatus.COMPLETED:
                    assessment.completed_at = datetime.now() - timedelta(days=random.randint(1, 30))
                elif assess_data["status"] == AssessmentStatus.ARCHIVED:
                    assessment.completed_at = datetime.now() - timedelta(days=random.randint(60, 180))
                    assessment.reviewed_by = admin.id
                db.add(assessment)
                assessments.append(assessment)
        db.commit()
        print(f"✅ 已创建 {len(assessments)} 个风险评估")
        print(f"   - PIA: {len([a for a in assessments if a.assessment_type == 'PIA'])} 个")
        print(f"   - DPIA: {len([a for a in assessments if a.assessment_type == 'DPIA'])} 个")
        print(f"   - 草稿: {len([a for a in assessments if a.status == AssessmentStatus.DRAFT])} 个")
        print(f"   - 进行中: {len([a for a in assessments if a.status == AssessmentStatus.IN_PROGRESS])} 个")
        print(f"   - 已完成: {len([a for a in assessments if a.status == AssessmentStatus.COMPLETED])} 个")
        print(f"   - 已归档: {len([a for a in assessments if a.status == AssessmentStatus.ARCHIVED])} 个")
        
        # 6. 创建丰富的传输审批（覆盖所有审批状态）
        print("\n[6/7] 创建丰富的传输审批...")
        approval_statuses = [ApprovalStatus.PENDING, ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.CANCELLED]
        transfer_types = ["API", "文件", "数据库"]
        
        approvals_data = [
            {"scen": "SCEN_001", "status": ApprovalStatus.APPROVED, "type": "API", "assets": [1, 2], "volume": 480000, "days": 20},
            {"scen": "SCEN_001", "status": ApprovalStatus.APPROVED, "type": "文件", "assets": [1], "volume": 200000, "days": 10},
            {"scen": "SCEN_002", "status": ApprovalStatus.PENDING, "type": "API", "assets": [3, 4], "volume": None, "days": 0},
            {"scen": "SCEN_004", "status": ApprovalStatus.APPROVED, "type": "API", "assets": [5, 6], "volume": 140000, "days": 5},
            {"scen": "SCEN_005", "status": ApprovalStatus.APPROVED, "type": "数据库", "assets": [7, 8], "volume": 280000, "days": 3},
            {"scen": "SCEN_006", "status": ApprovalStatus.REJECTED, "type": "文件", "assets": [9, 10], "volume": None, "days": 0},
            {"scen": "SCEN_007", "status": ApprovalStatus.APPROVED, "type": "API", "assets": [11, 12], "volume": 380000, "days": 90},
            {"scen": "SCEN_008", "status": ApprovalStatus.CANCELLED, "type": "API", "assets": [13, 14], "volume": None, "days": 0},
            {"scen": "SCEN_009", "status": ApprovalStatus.PENDING, "type": "实时", "assets": [15, 16], "volume": None, "days": 0},
            {"scen": "SCEN_010", "status": ApprovalStatus.APPROVED, "type": "文件", "assets": [17, 18], "volume": 110000, "days": 2},
        ]
        
        approvals = []
        for appr_data in approvals_data:
            approval = TransferApproval(
                scenario_id=scenarios_dict.get(appr_data["scen"], 1),
                approval_status=appr_data["status"],
                applicant_id=admin.id,
                transfer_type=appr_data["type"],
                data_assets=json.dumps(appr_data["assets"]),
            )
            if appr_data["status"] == ApprovalStatus.APPROVED:
                approval.approver_id = admin.id
                approval.approved_at = datetime.now() - timedelta(days=appr_data["days"])
                approval.transfer_start_time = datetime.now() - timedelta(days=appr_data["days"])
                approval.transfer_end_time = datetime.now() - timedelta(days=appr_data["days"] - 1)
                approval.actual_volume = Decimal(str(appr_data["volume"])) if appr_data["volume"] else None
                approval.approval_comment = "已批准，数据已脱敏处理"
            elif appr_data["status"] == ApprovalStatus.REJECTED:
                approval.approver_id = admin.id
                approval.rejected_reason = "不符合数据出境合规要求"
            elif appr_data["status"] == ApprovalStatus.CANCELLED:
                approval.approval_comment = "申请人主动取消"
            
            db.add(approval)
            approvals.append(approval)
        db.commit()
        print(f"✅ 已创建 {len(approvals)} 个传输审批")
        print(f"   - 待审批: {len([a for a in approvals if a.approval_status == ApprovalStatus.PENDING])} 个")
        print(f"   - 已批准: {len([a for a in approvals if a.approval_status == ApprovalStatus.APPROVED])} 个")
        print(f"   - 已拒绝: {len([a for a in approvals if a.approval_status == ApprovalStatus.REJECTED])} 个")
        print(f"   - 已取消: {len([a for a in approvals if a.approval_status == ApprovalStatus.CANCELLED])} 个")
        
        # 7. 创建丰富的审计日志（覆盖所有操作类型）
        print("\n[7/7] 创建丰富的审计日志...")
        audit_actions = [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE, AuditAction.APPROVE, AuditAction.REJECT, AuditAction.TRANSFER, AuditAction.INTERCEPT, AuditAction.DESENSITIZE, AuditAction.VIEW, AuditAction.EXPORT]
        resource_types = ["数据资产", "场景", "审批", "风险评估"]
        
        logs_data = [
            {"action": AuditAction.CREATE, "resource": "数据资产", "rid": 1, "days": 60, "details": {"asset_name": "DWS_CUST_ALL"}},
            {"action": AuditAction.UPDATE, "resource": "数据资产", "rid": 1, "days": 55, "details": {"field": "description"}},
            {"action": AuditAction.VIEW, "resource": "数据资产", "rid": 1, "days": 50, "details": {}},
            {"action": AuditAction.APPROVE, "resource": "场景", "rid": scenarios_dict.get("SCEN_001", 1), "days": 30, "details": {"scenario_code": "SCEN_001"}},
            {"action": AuditAction.TRANSFER, "resource": "审批", "rid": 1, "days": 20, "volume": 480000, "country": "美国", "status": "成功"},
            {"action": AuditAction.TRANSFER, "resource": "审批", "rid": 2, "days": 10, "volume": 200000, "country": "美国", "status": "成功"},
            {"action": AuditAction.VIEW, "resource": "风险评估", "rid": 1, "days": 5, "details": {}},
            {"action": AuditAction.INTERCEPT, "resource": "审批", "rid": 3, "days": 2, "status": "拦截", "anomaly": True, "type": "未授权传输", "reason": "传输申请未批准"},
            {"action": AuditAction.DESENSITIZE, "resource": "数据资产", "rid": 1, "days": 1, "details": {"method": "masking"}},
            {"action": AuditAction.EXPORT, "resource": "数据资产", "rid": 1, "days": 1, "details": {"format": "CSV"}},
            {"action": AuditAction.CREATE, "resource": "场景", "rid": scenarios_dict.get("SCEN_002", 2), "days": 15, "details": {"scenario_code": "SCEN_002"}},
            {"action": AuditAction.REJECT, "resource": "审批", "rid": 6, "days": 3, "details": {"reason": "不符合合规要求"}},
            {"action": AuditAction.UPDATE, "resource": "风险评估", "rid": 2, "days": 8, "details": {"field": "overall_score"}},
            {"action": AuditAction.TRANSFER, "resource": "审批", "rid": 4, "days": 5, "volume": 140000, "country": "新加坡", "status": "成功"},
            {"action": AuditAction.VIEW, "resource": "场景", "rid": scenarios_dict.get("SCEN_003", 3), "days": 12, "details": {}},
            {"action": AuditAction.DELETE, "resource": "数据资产", "rid": 20, "days": 7, "details": {"asset_code": "FILE_FIN_STATEMENT"}},
            {"action": AuditAction.APPROVE, "resource": "审批", "rid": 7, "days": 90, "details": {"approval_id": 7}},
            {"action": AuditAction.TRANSFER, "resource": "审批", "rid": 5, "days": 3, "volume": 280000, "country": "日本", "status": "成功"},
            {"action": AuditAction.INTERCEPT, "resource": "审批", "rid": 9, "days": 1, "status": "拦截", "anomaly": True, "type": "异常传输", "reason": "传输频率异常"},
            {"action": AuditAction.EXPORT, "resource": "风险评估", "rid": 3, "days": 4, "details": {"format": "PDF"}},
        ]
        
        logs = []
        for log_data in logs_data:
            log = AuditLog(
                action=log_data["action"],
                resource_type=log_data["resource"],
                resource_id=log_data["rid"],
                user_id=admin.id,
                username=admin.username,
                ip_address=f"192.168.1.{random.randint(100, 200)}",
                operation_details=log_data.get("details", {}),
                created_at=datetime.now() - timedelta(days=log_data["days"])
            )
            if log_data["action"] == AuditAction.TRANSFER:
                log.transfer_volume = Decimal(str(log_data.get("volume", 0)))
                log.destination_country = log_data.get("country", "未知")
                log.transfer_status = log_data.get("status", "成功")
            if log_data.get("anomaly"):
                log.is_anomaly = True
                log.anomaly_type = log_data.get("type", "未知异常")
                log.anomaly_reason = log_data.get("reason", "未知原因")
            
            db.add(log)
            logs.append(log)
        db.commit()
        print(f"✅ 已创建 {len(logs)} 条审计日志")
        print(f"   - 创建: {len([l for l in logs if l.action == AuditAction.CREATE])} 条")
        print(f"   - 更新: {len([l for l in logs if l.action == AuditAction.UPDATE])} 条")
        print(f"   - 删除: {len([l for l in logs if l.action == AuditAction.DELETE])} 条")
        print(f"   - 审批: {len([l for l in logs if l.action == AuditAction.APPROVE])} 条")
        print(f"   - 拒绝: {len([l for l in logs if l.action == AuditAction.REJECT])} 条")
        print(f"   - 传输: {len([l for l in logs if l.action == AuditAction.TRANSFER])} 条")
        print(f"   - 拦截: {len([l for l in logs if l.action == AuditAction.INTERCEPT])} 条")
        print(f"   - 脱敏: {len([l for l in logs if l.action == AuditAction.DESENSITIZE])} 条")
        print(f"   - 查看: {len([l for l in logs if l.action == AuditAction.VIEW])} 条")
        print(f"   - 导出: {len([l for l in logs if l.action == AuditAction.EXPORT])} 条")
        
        print("\n" + "=" * 60)
        print("✅ 丰富的演示数据创建完成！")
        print("=" * 60)
        print(f"\n📊 数据统计：")
        print(f"   - 数据分类: {len(classifications)} 个")
        print(f"   - 敏感标签: {len(tags)} 个")
        print(f"   - 数据资产: {len(assets)} 个（表/视图/接口/文件，所有级别，启用/禁用）")
        print(f"   - 跨境场景: {len(scenarios)} 个（所有状态、业务类型、传输频率）")
        print(f"   - 风险评估: {len(assessments)} 个（PIA/DPIA，所有状态和风险级别）")
        print(f"   - 传输审批: {len(approvals)} 个（所有审批状态）")
        print(f"   - 审计日志: {len(logs)} 条（所有操作类型）")
        print("\n💡 提示：现在可以刷新前端页面查看丰富的数据展示！")
        
    except Exception as e:
        print(f"\n❌ 创建演示数据失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_rich_demo_data()

