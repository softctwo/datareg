# 项目常用命令

## 开发环境启动

### 一键启动（推荐）
```bash
./start.sh
```

### 手动启动步骤

#### 1. 数据库初始化
```bash
cd backend
python3 create_db.py      # 创建数据库（如果不存在）
python3 init_db.py         # 初始化表结构
python3 init_users.py      # 创建默认用户
python3 init_demo_data.py  # 创建演示数据（可选）
```

#### 2. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 3. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

## 开发工具命令

### 数据库相关
```bash
cd backend

# 创建新的数据库迁移
alembic revision --autogenerate -m "描述信息"

# 应用数据库迁移
alembic upgrade head

# 查看迁移历史
alembic history

# 回滚迁移
alembic downgrade -1
```

### 后端开发
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black .

# 类型检查
mypy .

# 安全检查
bandit -r .
```

### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 类型检查
npx tsc --noEmit
```

## 系统维护

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看数据库日志
tail -f logs/db.log

# 查看错误日志
tail -f logs/error.log
```

### 数据备份
```bash
# 备份数据库
pg_dump -h localhost -U postgres -d datareg > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
psql -h localhost -U postgres -d datareg < backup_20241201_120000.sql
```

### 性能监控
```bash
# 查看系统资源
top
htop

# 查看端口占用
lsof -i :8000  # 后端端口
lsof -i :3000  # 前端端口

# 查看进程
ps aux | grep uvicorn
ps aux | grep node
```

## Git工作流

### 基本操作
```bash
# 查看状态
git status

# 添加文件
git add .

# 提交代码
git commit -m "feat: 添加新功能"

# 推送代码
git push

# 拉取最新代码
git pull
```

### 分支管理
```bash
# 创建新分支
git checkout -b feature/新功能名称

# 切换分支
git checkout main

# 合并分支
git merge feature/新功能名称

# 删除分支
git branch -d feature/新功能名称
```

## 部署相关

### 停止服务
```bash
./stop.sh
```

### 重启服务
```bash
./stop.sh
./start.sh
```

### 查看服务状态
```bash
# 检查后端服务
curl http://localhost:8000/api/v1/health

# 检查前端服务
curl http://localhost:3000

# 检查数据库连接
psql -h localhost -U postgres -d datareg -c "SELECT version();"
```

## 常见问题解决

### 数据库连接问题
```bash
# 检查PostgreSQL服务状态
brew services list | grep postgresql

# 启动PostgreSQL服务
brew services start postgresql

# 检查连接
psql -h localhost -U postgres -d datareg
```

### 端口占用问题
```bash
# 查找占用8000端口的进程
lsof -ti:8000

# 终止进程
kill -9 $(lsof -ti:8000)
```

### 依赖问题
```bash
# 清理npm缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install

# 清理pip缓存
pip cache purge

# 重新安装Python依赖
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 监控命令

### 实时监控日志
```bash
# 监控后端日志
tail -f backend/logs/app.log

# 监控错误日志
tail -f backend/logs/error.log

# 监控访问日志
tail -f backend/logs/access.log
```

### 数据库监控
```bash
# 查看活动连接
psql -h localhost -U postgres -d datareg -c "SELECT * FROM pg_stat_activity;"

# 查看表大小
psql -h localhost -U postgres -d datareg -c "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables WHERE schemaname = 'public';"
```

## API测试

### 使用curl测试API
```bash
# 登录获取token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 使用token访问API
curl -X GET "http://localhost:8000/api/v1/data-assets" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### API文档
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc