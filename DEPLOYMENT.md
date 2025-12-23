# 部署文档

## 系统要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- npm 或 yarn

## 后端部署

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

确保PostgreSQL服务已启动，并创建数据库：

```sql
CREATE DATABASE datareg;
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置数据库连接信息。

### 4. 初始化数据库

```bash
python init_db.py
```

或使用Alembic迁移：

```bash
alembic upgrade head
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

服务将在 `http://localhost:8000` 启动。

API文档访问：`http://localhost:8000/api/docs`

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动。

### 3. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

## Docker部署（可选）

### 后端Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端Dockerfile

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

## 生产环境注意事项

1. **安全配置**
   - 修改 `SECRET_KEY` 为强随机字符串
   - 配置HTTPS
   - 设置CORS白名单

2. **数据库**
   - 使用连接池
   - 定期备份
   - 配置读写分离（如需要）

3. **监控**
   - 配置日志收集
   - 设置告警规则
   - 监控系统性能

4. **高可用**
   - 使用负载均衡
   - 配置多实例
   - 设置健康检查

## 常见问题

### 数据库连接失败

检查：
- PostgreSQL服务是否启动
- 数据库连接信息是否正确
- 防火墙设置

### 前端无法连接后端

检查：
- 后端服务是否启动
- CORS配置是否正确
- 代理配置是否正确

## 作者

张彦龙

