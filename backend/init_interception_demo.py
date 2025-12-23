"""
初始化拦截与脱敏演示数据
作者：张彦龙
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.models.data_asset import DataAsset, DataLevel
from app.models.scenario import CrossBorderScenario, TransferApproval, ApprovalStatus, ScenarioStatus
from app.models.risk import RiskAssessment, AssessmentStatus
from datetime import datetime, timedelta
from decimal import Decimal
import json

def init_interception_demo():
    """初始化拦截与脱敏演示数据"""
    db = SessionLocal()
    try:
        # 获取管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("请先运行 init_users.py 创建用户")
            return
        
        print("开始创建拦截与脱敏演示数据...")
        
        # 1. 确保有一些数据资产
        print("检查数据资产...")
        assets = db.query(DataAsset).limit(10).all()
        if len(assets) < 3:
            print("数据资产不足，请先运行 init_demo_data.py 创建数据资产")
            return
        
        # 2. 创建一些已批准的传输审批（用于白名单展示）
        print("创建已批准的传输审批（白名单数据）...")
        
        # 获取一些场景
        scenarios = db.query(CrossBorderScenario).limit(5).all()
        if not scenarios:
            # 如果没有场景，创建一些
            scenarios = []
            for i in range(3):
                scenario = CrossBorderScenario(
                    scenario_name=f"演示场景-数据传输{i+1}",
                    scenario_code=f"DEMO_SCENARIO_{i+1}",
                    description=f"用于演示的跨境数据传输场景{i+1}",
                    source_country="中国",
                    destination_country=["美国", "新加坡", "日本"][i % 3],
                    transfer_purpose="业务分析",
                    data_volume=1000000 + i * 100000,
                    transfer_method="API接口",
                    status=ScenarioStatus.APPROVED,
                    applicant_id=admin.id,
                    created_at=datetime.now() - timedelta(days=30-i*5)
                )
                db.add(scenario)
                db.flush()
                scenarios.append(scenario)
        
        # 创建已批准的审批
        approved_approvals = []
        for i, scenario in enumerate(scenarios[:3]):
            # 获取场景关联的资产ID
            asset_ids = [assets[i % len(assets)].id, assets[(i+1) % len(assets)].id]
            
            approval = TransferApproval(
                scenario_id=scenario.id,
                approval_status=ApprovalStatus.APPROVED,
                applicant_id=admin.id,
                approver_id=admin.id,
                transfer_type="API接口",
                transfer_start_time=datetime.now() - timedelta(days=20-i*3),
                transfer_end_time=datetime.now() + timedelta(days=30-i*3),
                actual_volume=500000 + i * 50000,
                approval_comment=f"演示审批{i+1}，已批准",
                approved_at=datetime.now() - timedelta(days=20-i*3),
                data_assets=json.dumps(asset_ids),
                created_at=datetime.now() - timedelta(days=25-i*3)
            )
            db.add(approval)
            approved_approvals.append(approval)
        
        db.flush()
        
        # 3. 将已批准的审批添加到白名单（通过服务）
        print("添加到白名单...")
        from app.services.interception_service import InterceptionService
        interception_service = InterceptionService(db)
        for approval in approved_approvals:
            interception_service.add_to_whitelist(approval)
        
        # 4. 添加一些资产到黑名单（用于展示）
        print("添加资产到黑名单...")
        # 选择一些敏感数据资产添加到黑名单
        sensitive_assets = [a for a in assets if a.data_level in [DataLevel.SENSITIVE, DataLevel.IMPORTANT]][:2]
        for asset in sensitive_assets:
            interception_service.add_to_blacklist(asset.id)
        
        db.commit()
        
        print(f"✅ 拦截与脱敏演示数据创建完成！")
        print(f"   - 已创建 {len(approved_approvals)} 个已批准的审批（白名单）")
        print(f"   - 已添加 {len(sensitive_assets)} 个资产到黑名单")
        print(f"   - 可以在拦截与脱敏管理页面查看效果")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_interception_demo()

