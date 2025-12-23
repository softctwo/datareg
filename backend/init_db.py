"""
数据库初始化脚本
作者：张彦龙
"""
from app.core.database import engine, Base
from app.models import *  # 导入所有模型
from app.core.config import settings

def init_database():
    """初始化数据库表结构"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print(f"数据库连接: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'N/A'}")

if __name__ == "__main__":
    init_database()

