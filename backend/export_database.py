"""
导出数据库建库和初始化数据脚本
作者：张彦龙
"""
import os
from datetime import datetime
from sqlalchemy import text, inspect
from app.core.database import engine, Base
from app.core.config import settings
from app.models import *  # 导入所有模型

def escape_string(value):
    """转义字符串值"""
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return "'" + value.replace("'", "''").replace("\\", "\\\\") + "'"
    return str(value)

def export_database():
    """导出数据库结构和数据"""
    print("=" * 60)
    print("开始导出数据库...")
    print("=" * 60)
    
    # 创建导出目录
    export_dir = "database_export"
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 使用 Alembic 生成结构，或者直接使用 SQLAlchemy 的 create_all
    print("\n[1/3] 导出数据库结构（DDL）...")
    schema_file = f"{export_dir}/01_schema_{timestamp}.sql"
    try:
        # 使用 SQLAlchemy 生成 CREATE TABLE 语句
        from sqlalchemy.schema import CreateTable
        
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write("-- ============================================\n")
            f.write("-- 数据库结构脚本（DDL）\n")
            f.write(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- ============================================\n\n")
            
            # 获取所有表
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # 为每个表生成 CREATE TABLE 语句
            for table_name in sorted(tables):
                f.write(f"\n-- 表: {table_name}\n")
                f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n\n")
                
                # 使用 information_schema 生成 CREATE TABLE 语句
                with engine.connect() as conn:
                    # 获取列信息
                    columns = inspector.get_columns(table_name)
                    f.write(f"CREATE TABLE {table_name} (\n")
                    col_defs = []
                    for col in columns:
                        col_name = col['name']
                        col_type = str(col['type'])
                        nullable = "NULL" if col['nullable'] else "NOT NULL"
                        default = ""
                        if col.get('default'):
                            default_val = col['default']
                            if isinstance(default_val, str) and 'nextval' in default_val:
                                # 序列默认值
                                default = f" DEFAULT {default_val}"
                            elif isinstance(default_val, str):
                                default = f" DEFAULT {escape_string(default_val)}"
                            else:
                                default = f" DEFAULT {default_val}"
                        col_defs.append(f"    {col_name} {col_type} {nullable}{default}")
                    f.write(",\n".join(col_defs))
                    f.write("\n);\n\n")
        
        print(f"✅ 数据库结构已导出到: {schema_file}")
    except Exception as e:
        print(f"❌ 导出数据库结构失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. 导出数据（DML）
    print("\n[2/3] 导出数据库数据（DML）...")
    data_file = f"{export_dir}/02_data_{timestamp}.sql"
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write("-- ============================================\n")
                f.write("-- 数据库数据脚本（DML）\n")
                f.write(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-- ============================================\n\n")
                
                # 按依赖顺序导出表
                table_order = [
                    'users', 'roles', 'user_role',
                    'data_classifications', 'sensitive_tags',
                    'data_assets', 'asset_tag_association',
                    'cross_border_scenarios',
                    'risk_assessments',
                    'transfer_approvals',
                    'notifications',
                    'system_configs',
                    'audit_logs'
                ]
                
                # 只导出存在的表
                tables_to_export = [t for t in table_order if t in tables]
                # 添加其他表
                tables_to_export.extend([t for t in tables if t not in tables_to_export])
                
                for table_name in tables_to_export:
                    f.write(f"\n-- 表: {table_name}\n")
                    f.write(f"TRUNCATE TABLE {table_name} CASCADE;\n\n")
                    
                    # 获取表的所有列
                    columns = inspector.get_columns(table_name)
                    column_names = [col['name'] for col in columns]
                    
                    # 查询数据
                    select_sql = text(f'SELECT * FROM "{table_name}"')
                    result = conn.execute(select_sql)
                    rows = result.fetchall()
                    
                    if rows:
                        # 生成 INSERT 语句
                        for row in rows:
                            values = []
                            for i, col in enumerate(columns):
                                value = row[i]
                                
                                if value is None:
                                    values.append("NULL")
                                elif isinstance(value, str):
                                    values.append(escape_string(value))
                                elif isinstance(value, bool):
                                    values.append("TRUE" if value else "FALSE")
                                elif isinstance(value, (int, float)):
                                    values.append(str(value))
                                elif hasattr(value, '__str__'):
                                    # 处理 Decimal, datetime 等类型
                                    if 'Decimal' in str(type(value)):
                                        values.append(str(value))
                                    elif 'datetime' in str(type(value)):
                                        values.append(escape_string(value.isoformat()))
                                    else:
                                        values.append(escape_string(str(value)))
                                else:
                                    values.append(escape_string(str(value)))
                            
                            columns_str = ", ".join([f'"{col}"' for col in column_names])
                            values_str = ", ".join(values)
                            f.write(f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({values_str});\n')
                    else:
                        f.write(f"-- 表 {table_name} 无数据\n")
        
        print(f"✅ 数据库数据已导出到: {data_file}")
    except Exception as e:
        print(f"❌ 导出数据库数据失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 合并为完整的初始化脚本
    print("\n[3/3] 生成完整的初始化脚本...")
    init_file = f"{export_dir}/init_database_{timestamp}.sql"
    try:
        with open(init_file, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write("-- ============================================\n")
            f.write("-- 银行重要数据跨境数据管控系统\n")
            f.write("-- 数据库初始化脚本\n")
            f.write(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- 作者: 张彦龙\n")
            f.write("-- ============================================\n\n")
            
            # 写入数据库创建语句
            f.write("-- 创建数据库（如果不存在）\n")
            f.write(f"-- CREATE DATABASE {settings.POSTGRES_DB};\n")
            f.write(f"-- \\c {settings.POSTGRES_DB};\n\n")
            
            # 写入结构
            f.write("-- ============================================\n")
            f.write("-- 第一部分：数据库结构（DDL）\n")
            f.write("-- ============================================\n\n")
            with open(schema_file, 'r', encoding='utf-8') as sf:
                f.write(sf.read())
            
            f.write("\n\n")
            
            # 写入数据
            f.write("-- ============================================\n")
            f.write("-- 第二部分：初始化数据（DML）\n")
            f.write("-- ============================================\n\n")
            with open(data_file, 'r', encoding='utf-8') as df:
                f.write(df.read())
            
            f.write("\n\n")
            f.write("-- ============================================\n")
            f.write("-- 初始化完成\n")
            f.write("-- ============================================\n")
        
        print(f"✅ 完整初始化脚本已生成: {init_file}")
    except Exception as e:
        print(f"❌ 生成完整脚本失败: {e}")
        return
    
    # 4. 生成使用说明
    readme_file = f"{export_dir}/README_{timestamp}.md"
    try:
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write("# 数据库导出文件说明\n\n")
            f.write(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 文件说明\n\n")
            f.write("1. **01_schema_*.sql** - 数据库结构脚本（DDL）\n")
            f.write("   - 包含所有表的创建语句\n")
            f.write("   - 包含索引、约束等\n\n")
            f.write("2. **02_data_*.sql** - 数据库数据脚本（DML）\n")
            f.write("   - 包含所有表的 INSERT 语句\n")
            f.write("   - 包含所有初始化数据\n\n")
            f.write("3. **init_database_*.sql** - 完整初始化脚本\n")
            f.write("   - 包含结构+数据的完整脚本\n")
            f.write("   - 可以直接用于初始化新数据库\n\n")
            f.write("## 使用方法\n\n")
            f.write("### 方法一：使用完整脚本（推荐）\n\n")
            f.write("```bash\n")
            f.write(f"# 1. 创建数据库\n")
            f.write(f"psql -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -d postgres -c \"CREATE DATABASE {settings.POSTGRES_DB};\"\n\n")
            f.write(f"# 2. 执行初始化脚本\n")
            f.write(f"psql -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -d {settings.POSTGRES_DB} -f init_database_{timestamp}.sql\n")
            f.write("```\n\n")
            f.write("### 方法二：分步执行\n\n")
            f.write("```bash\n")
            f.write(f"# 1. 创建数据库\n")
            f.write(f"psql -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -d postgres -c \"CREATE DATABASE {settings.POSTGRES_DB};\"\n\n")
            f.write(f"# 2. 执行结构脚本\n")
            f.write(f"psql -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -d {settings.POSTGRES_DB} -f 01_schema_{timestamp}.sql\n\n")
            f.write(f"# 3. 执行数据脚本\n")
            f.write(f"psql -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -d {settings.POSTGRES_DB} -f 02_data_{timestamp}.sql\n")
            f.write("```\n\n")
            f.write("## 数据库信息\n\n")
            f.write(f"- **数据库名**: {settings.POSTGRES_DB}\n")
            f.write(f"- **服务器**: {settings.POSTGRES_SERVER}\n")
            f.write(f"- **用户**: {settings.POSTGRES_USER}\n\n")
            f.write("## 注意事项\n\n")
            f.write("1. 执行脚本前请确保 PostgreSQL 服务正在运行\n")
            f.write("2. 如果数据库已存在，请先备份或删除\n")
            f.write("3. 执行脚本时请确保有足够的权限\n")
            f.write("4. 建议在生产环境使用前先在测试环境验证\n\n")
        
        print(f"✅ 使用说明已生成: {readme_file}")
    except Exception as e:
        print(f"⚠️  生成使用说明失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 数据库导出完成！")
    print("=" * 60)
    print(f"\n📁 导出目录: {export_dir}/")
    print(f"📄 文件列表:")
    print(f"   - 01_schema_{timestamp}.sql (数据库结构)")
    print(f"   - 02_data_{timestamp}.sql (数据库数据)")
    print(f"   - init_database_{timestamp}.sql (完整初始化脚本)")
    print(f"   - README_{timestamp}.md (使用说明)")
    print(f"\n💡 提示: 可以使用 init_database_{timestamp}.sql 文件来初始化新数据库")

if __name__ == "__main__":
    export_database()
