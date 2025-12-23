"""
初始化通知演示数据
作者：张彦龙
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.models.notification import Notification, NotificationType, NotificationStatus
from datetime import datetime, timedelta

def init_notification_demo():
    """初始化通知演示数据"""
    db = SessionLocal()
    try:
        # 获取管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("请先运行 init_users.py 创建用户")
            return
        
        print("开始创建通知演示数据...")
        
        # 创建一些演示通知
        notifications = [
            Notification(
                user_id=admin.id,
                type=NotificationType.APPROVAL_PENDING,
                title="传输审批待处理",
                content="您有1个传输审批申请待处理，请及时审批。",
                status=NotificationStatus.UNREAD,
                resource_type="approval",
                resource_id=1,
                action_url="/approvals",
                priority=1,
                is_read=False,
                created_at=datetime.now() - timedelta(hours=2)
            ),
            Notification(
                user_id=admin.id,
                type=NotificationType.THRESHOLD_WARNING,
                title="个人信息阈值预警",
                content="风险评估 #RA001 的个人信息数量已超过阈值，请及时处理。",
                status=NotificationStatus.UNREAD,
                resource_type="risk_assessment",
                resource_id=1,
                action_url="/risk-assessments",
                priority=2,
                is_read=False,
                created_at=datetime.now() - timedelta(hours=5)
            ),
            Notification(
                user_id=admin.id,
                type=NotificationType.ANOMALY_ALERT,
                title="异常行为检测",
                content="检测到异常的数据传输行为，请立即查看审计日志。",
                status=NotificationStatus.UNREAD,
                resource_type="audit",
                resource_id=1,
                action_url="/audit-logs",
                priority=2,
                is_read=False,
                created_at=datetime.now() - timedelta(days=1)
            ),
            Notification(
                user_id=admin.id,
                type=NotificationType.SYSTEM_NOTICE,
                title="系统维护通知",
                content="系统将于今晚22:00-24:00进行维护，期间可能无法访问。",
                status=NotificationStatus.READ,
                priority=0,
                is_read=True,
                read_at=datetime.now() - timedelta(hours=10),
                created_at=datetime.now() - timedelta(days=2)
            ),
            Notification(
                user_id=admin.id,
                type=NotificationType.REMINDER,
                title="数据资产扫描提醒",
                content="提醒：本周的数据资产扫描任务尚未完成，请及时处理。",
                status=NotificationStatus.UNREAD,
                resource_type="data_asset",
                action_url="/data-assets",
                priority=0,
                is_read=False,
                created_at=datetime.now() - timedelta(days=3)
            )
        ]
        
        # 检查是否已存在通知
        existing_count = db.query(Notification).filter(Notification.user_id == admin.id).count()
        if existing_count == 0:
            for notification in notifications:
                db.add(notification)
            db.commit()
            print(f"✅ 已创建 {len(notifications)} 条通知演示数据")
        else:
            print(f"⚠️  已存在 {existing_count} 条通知，跳过创建")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_notification_demo()

