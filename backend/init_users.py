"""
初始化用户脚本
作者：张彦龙
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def init_users():
    """初始化默认用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@datareg.com",
                full_name="系统管理员",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            print("创建管理员用户: admin / admin123")
        
        # 检查是否已存在测试用户
        test_user = db.query(User).filter(User.username == "test").first()
        if not test_user:
            test_user = User(
                username="test",
                email="test@datareg.com",
                full_name="测试用户",
                hashed_password=get_password_hash("test123"),
                is_active=True,
                is_superuser=False
            )
            db.add(test_user)
            print("创建测试用户: test / test123")
        
        db.commit()
        print("用户初始化完成！")
    except Exception as e:
        print(f"初始化用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_users()

