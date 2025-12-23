"""
初始化演示数据
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

def init_demo_data():
    """初始化演示数据"""
    db = SessionLocal()
    try:
        # 获取管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("请先运行 init_users.py 创建用户")
            return
        
        print("开始创建演示数据...")
        
        # 1. 创建数据分类
        print("创建数据分类...")
        classifications = [
            DataClassification(
                category_name="客户信息",
                category_code="CUST_INFO",
                level=1,
                description="客户相关数据"
            ),
            DataClassification(
                category_name="交易数据",
                category_code="TRAN_DATA",
                level=1,
                description="交易相关数据"
            ),
            DataClassification(
                category_name="风险数据",
                category_code="RISK_DATA",
                level=1,
                description="风险相关数据"
            ),
            DataClassification(
                category_name="财务数据",
                category_code="FIN_DATA",
                level=1,
                description="财务相关数据"
            )
        ]
        for cls in classifications:
            existing = db.query(DataClassification).filter(
                DataClassification.category_code == cls.category_code
            ).first()
            if not existing:
                db.add(cls)
        db.commit()
        
        # 获取分类ID
        cust_class = db.query(DataClassification).filter(
            DataClassification.category_code == "CUST_INFO"
        ).first()
        tran_class = db.query(DataClassification).filter(
            DataClassification.category_code == "TRAN_DATA"
        ).first()
        risk_class = db.query(DataClassification).filter(
            DataClassification.category_code == "RISK_DATA"
        ).first()
        
        # 2. 创建敏感标签
        print("创建敏感标签...")
        tags = [
            SensitiveTag(
                tag_name="身份证号",
                tag_code="ID_CARD",
                tag_type="PII",
                detection_rule="ID_NO|IDNO|身份证",
                risk_level="高",
                description="身份证号码标识"
            ),
            SensitiveTag(
                tag_name="手机号",
                tag_code="MOBILE",
                tag_type="PII",
                detection_rule="MOB_NO|MOBILE|手机",
                risk_level="高",
                description="手机号码标识"
            ),
            SensitiveTag(
                tag_name="银行卡号",
                tag_code="BANK_CARD",
                tag_type="PII",
                detection_rule="CARD_NO|ACCT_NO|银行卡",
                risk_level="高",
                description="银行卡号标识"
            ),
            SensitiveTag(
                tag_name="信贷总量",
                tag_code="CREDIT_TOTAL",
                tag_type="重要数据",
                detection_rule="信贷总量|CREDIT_TOTAL",
                risk_level="中",
                description="信贷总量数据"
            )
        ]
        for tag in tags:
            existing = db.query(SensitiveTag).filter(
                SensitiveTag.tag_code == tag.tag_code
            ).first()
            if not existing:
                db.add(tag)
        db.commit()
        
        # 3. 创建数据资产
        print("创建数据资产...")
        assets = [
            DataAsset(
                asset_name="DWS_CUST_ALL",
                asset_code="DWS_CUST_ALL",
                asset_type="表",
                source_system="数据仓库",
                schema_name="dws",
                table_name="cust_all",
                data_level=DataLevel.SENSITIVE,
                classification_id=cust_class.id if cust_class else None,
                field_count=25,
                record_count=1000000,
                description="全量客户信息表，包含客户基本信息和联系方式"
            ),
            DataAsset(
                asset_name="DWS_FINA_GL",
                asset_code="DWS_FINA_GL",
                asset_type="表",
                source_system="数据仓库",
                schema_name="dws",
                table_name="fina_gl",
                data_level=DataLevel.IMPORTANT,
                classification_id=risk_class.id if risk_class else None,
                field_count=30,
                record_count=500000,
                description="总账表，包含财务科目和余额信息"
            ),
            DataAsset(
                asset_name="DWS_TRAN_ACCT_INNER_TX",
                asset_code="DWS_TRAN_ACCT_INNER_TX",
                asset_type="表",
                source_system="数据仓库",
                schema_name="dws",
                table_name="tran_acct_inner_tx",
                data_level=DataLevel.SENSITIVE,
                classification_id=tran_class.id if tran_class else None,
                field_count=20,
                record_count=5000000,
                description="内部账户交易明细表"
            ),
            DataAsset(
                asset_name="RISK_EXPOSURE_SUMMARY",
                asset_code="RISK_EXPOSURE_SUMMARY",
                asset_type="表",
                source_system="风险系统",
                schema_name="risk",
                table_name="exposure_summary",
                data_level=DataLevel.IMPORTANT,
                classification_id=risk_class.id if risk_class else None,
                field_count=15,
                record_count=100000,
                description="风险暴露汇总表，包含NON_REL_EXPOSURE_AMT字段"
            )
        ]
        for asset in assets:
            existing = db.query(DataAsset).filter(
                DataAsset.asset_code == asset.asset_code
            ).first()
            if not existing:
                db.add(asset)
        db.commit()
        
        # 4. 创建跨境场景
        print("创建跨境场景...")
        scenarios = [
            CrossBorderScenario(
                scenario_name="母行集团年度审计",
                scenario_code="SCEN_001",
                business_type="审计",
                recipient_name="母行总部",
                recipient_country="美国",
                recipient_type="母行",
                data_purpose="年度财务审计和合规审查",
                storage_duration=365,
                transfer_frequency="一次性",
                security_level="高",
                encryption_method="AES-256",
                data_scope="客户基本信息、交易汇总数据",
                estimated_volume=Decimal("500000"),
                status=ScenarioStatus.APPROVED,
                approver_id=admin.id,
                approved_at=datetime.now() - timedelta(days=30),
                expiry_date=datetime.now() + timedelta(days=335),
                created_by=admin.id
            ),
            CrossBorderScenario(
                scenario_name="跨境贸易融资合规审查",
                scenario_code="SCEN_002",
                business_type="合规审查",
                recipient_name="境外分行",
                recipient_country="新加坡",
                recipient_type="境外分行",
                data_purpose="跨境贸易融资业务合规性审查",
                storage_duration=180,
                transfer_frequency="月",
                security_level="中",
                encryption_method="AES-128",
                data_scope="贸易融资相关客户和交易数据",
                estimated_volume=Decimal("200000"),
                status=ScenarioStatus.PENDING,
                created_by=admin.id
            ),
            CrossBorderScenario(
                scenario_name="境外分行报表汇总",
                scenario_code="SCEN_003",
                business_type="报表汇总",
                recipient_name="亚太区总部",
                recipient_country="香港",
                recipient_type="境外分行",
                data_purpose="月度业务报表汇总",
                storage_duration=90,
                transfer_frequency="月",
                security_level="中",
                encryption_method="AES-128",
                data_scope="业务汇总数据，不含明细",
                estimated_volume=Decimal("100000"),
                status=ScenarioStatus.DRAFT,
                created_by=admin.id
            )
        ]
        for scenario in scenarios:
            existing = db.query(CrossBorderScenario).filter(
                CrossBorderScenario.scenario_code == scenario.scenario_code
            ).first()
            if not existing:
                db.add(scenario)
        db.commit()
        
        # 获取场景ID
        scenario1 = db.query(CrossBorderScenario).filter(
            CrossBorderScenario.scenario_code == "SCEN_001"
        ).first()
        scenario2 = db.query(CrossBorderScenario).filter(
            CrossBorderScenario.scenario_code == "SCEN_002"
        ).first()
        
        # 5. 创建风险评估
        print("创建风险评估...")
        assessments = [
            RiskAssessment(
                assessment_name="母行审计风险评估",
                assessment_code="RISK_001",
                assessment_type="PIA",
                scenario_id=scenario1.id if scenario1 else 1,
                legal_environment_score=Decimal("75.00"),
                data_volume_score=Decimal("60.00"),
                security_measures_score=Decimal("85.00"),
                data_sensitivity_score=Decimal("70.00"),
                personal_info_count=Decimal("500000"),
                sensitive_info_count=Decimal("100000"),
                exceeds_personal_threshold=False,
                exceeds_sensitive_threshold=True,
                overall_risk_level=RiskLevel.MEDIUM,
                overall_score=Decimal("72.50"),
                risk_factors={
                    "legal_environment": {"score": 75, "risk": "低"},
                    "data_volume": {"exceeds_personal": False, "exceeds_sensitive": True},
                    "security_measures": {"score": 85}
                },
                mitigation_measures="使用AES-256加密，实施数据脱敏，签署标准合同",
                assessment_result="中等风险，建议加强敏感数据保护措施",
                requires_regulatory_approval=True,
                recommendation="建议进行数据脱敏处理，并签署数据出境标准合同",
                status=AssessmentStatus.COMPLETED,
                assessor_id=admin.id,
                completed_at=datetime.now() - timedelta(days=25)
            ),
            RiskAssessment(
                assessment_name="跨境贸易融资风险评估",
                assessment_code="RISK_002",
                assessment_type="DPIA",
                scenario_id=scenario2.id if scenario2 else 2,
                legal_environment_score=Decimal("80.00"),
                data_volume_score=Decimal("50.00"),
                security_measures_score=Decimal("70.00"),
                data_sensitivity_score=Decimal("65.00"),
                personal_info_count=Decimal("200000"),
                sensitive_info_count=Decimal("50000"),
                exceeds_personal_threshold=False,
                exceeds_sensitive_threshold=False,
                overall_risk_level=RiskLevel.LOW,
                overall_score=Decimal("66.25"),
                risk_factors={
                    "legal_environment": {"score": 80, "risk": "低"},
                    "data_volume": {"exceeds_personal": False, "exceeds_sensitive": False},
                    "security_measures": {"score": 70}
                },
                mitigation_measures="使用AES-128加密，定期审查",
                assessment_result="低风险，可以批准",
                requires_regulatory_approval=False,
                recommendation="可以批准，建议定期审查",
                status=AssessmentStatus.COMPLETED,
                assessor_id=admin.id,
                completed_at=datetime.now() - timedelta(days=10)
            )
        ]
        for assessment in assessments:
            existing = db.query(RiskAssessment).filter(
                RiskAssessment.assessment_code == assessment.assessment_code
            ).first()
            if not existing:
                db.add(assessment)
        db.commit()
        
        # 6. 创建传输审批
        print("创建传输审批...")
        approvals = [
            TransferApproval(
                scenario_id=scenario1.id if scenario1 else 1,
                approval_status=ApprovalStatus.APPROVED,
                applicant_id=admin.id,
                approver_id=admin.id,
                transfer_type="API",
                data_assets=json.dumps([1, 2]),
                transfer_start_time=datetime.now() - timedelta(days=20),
                transfer_end_time=datetime.now() - timedelta(days=19),
                actual_volume=Decimal("480000"),
                approval_comment="已批准，数据已脱敏处理",
                approved_at=datetime.now() - timedelta(days=20)
            ),
            TransferApproval(
                scenario_id=scenario1.id if scenario1 else 1,
                approval_status=ApprovalStatus.APPROVED,
                applicant_id=admin.id,
                approver_id=admin.id,
                transfer_type="文件",
                data_assets=json.dumps([1]),
                transfer_start_time=datetime.now() - timedelta(days=10),
                transfer_end_time=datetime.now() - timedelta(days=9),
                actual_volume=Decimal("200000"),
                approval_comment="已批准",
                approved_at=datetime.now() - timedelta(days=10)
            ),
            TransferApproval(
                scenario_id=scenario2.id if scenario2 else 2,
                approval_status=ApprovalStatus.PENDING,
                applicant_id=admin.id,
                transfer_type="API",
                data_assets=json.dumps([3, 4])
            )
        ]
        for approval in approvals:
            db.add(approval)
        db.commit()
        
        # 7. 创建审计日志
        print("创建审计日志...")
        logs = [
            AuditLog(
                action=AuditAction.CREATE,
                resource_type="数据资产",
                resource_id=1,
                user_id=admin.id,
                username=admin.username,
                ip_address="192.168.1.100",
                operation_details={"asset_name": "DWS_CUST_ALL"},
                created_at=datetime.now() - timedelta(days=60)
            ),
            AuditLog(
                action=AuditAction.APPROVE,
                resource_type="场景",
                resource_id=scenario1.id if scenario1 else 1,
                user_id=admin.id,
                username=admin.username,
                ip_address="192.168.1.100",
                operation_details={"scenario_code": "SCEN_001"},
                created_at=datetime.now() - timedelta(days=30)
            ),
            AuditLog(
                action=AuditAction.TRANSFER,
                resource_type="审批",
                resource_id=1,
                user_id=admin.id,
                username=admin.username,
                ip_address="192.168.1.100",
                transfer_volume=Decimal("480000"),
                destination_country="美国",
                transfer_status="成功",
                created_at=datetime.now() - timedelta(days=20)
            ),
            AuditLog(
                action=AuditAction.TRANSFER,
                resource_type="审批",
                resource_id=2,
                user_id=admin.id,
                username=admin.username,
                ip_address="192.168.1.100",
                transfer_volume=Decimal("200000"),
                destination_country="美国",
                transfer_status="成功",
                created_at=datetime.now() - timedelta(days=10)
            ),
            AuditLog(
                action=AuditAction.VIEW,
                resource_type="风险评估",
                resource_id=1,
                user_id=admin.id,
                username=admin.username,
                ip_address="192.168.1.101",
                created_at=datetime.now() - timedelta(days=5)
            ),
            AuditLog(
                action=AuditAction.INTERCEPT,
                resource_type="审批",
                resource_id=3,
                user_id=admin.id,
                username=admin.username,
                ip_address="192.168.1.100",
                transfer_status="拦截",
                is_anomaly=True,
                anomaly_type="未授权传输",
                anomaly_reason="传输申请未批准",
                created_at=datetime.now() - timedelta(days=2)
            )
        ]
        for log in logs:
            db.add(log)
        db.commit()
        
        print("✅ 演示数据创建完成！")
        print(f"   - 数据分类: {len(classifications)} 个")
        print(f"   - 敏感标签: {len(tags)} 个")
        print(f"   - 数据资产: {len(assets)} 个")
        print(f"   - 跨境场景: {len(scenarios)} 个")
        print(f"   - 风险评估: {len(assessments)} 个")
        print(f"   - 传输审批: {len(approvals)} 个")
        print(f"   - 审计日志: {len(logs)} 条")
        
    except Exception as e:
        print(f"创建演示数据失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_demo_data()

