"""
创建数据库脚本
作者：张彦龙
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings

def create_database():
    """创建数据库"""
    try:
        # 连接到postgres数据库（默认数据库）
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database="postgres"  # 连接到默认数据库
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"数据库 '{settings.POSTGRES_DB}' 已存在")
        else:
            # 创建数据库
            cursor.execute(f'CREATE DATABASE {settings.POSTGRES_DB}')
            print(f"数据库 '{settings.POSTGRES_DB}' 创建成功！")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"创建数据库失败: {e}")
        print("\n请手动创建数据库：")
        print(f"psql -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER}")
        print(f"CREATE DATABASE {settings.POSTGRES_DB};")

if __name__ == "__main__":
    create_database()

