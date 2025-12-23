# 快速开始指南

## 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (已启动)

## 快速启动（推荐）

使用启动脚本一键启动：

```bash
./start.sh
```

## 手动启动

### 1. 后端启动

```bash
cd backend

# 创建虚拟环境（首次）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次）
python init_db.py

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 2. 前端启动

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

## 访问系统

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs

## 首次使用

1. **初始化数据库**
   ```bash
   cd backend
   python init_db.py
   ```

2. **初始化用户**
   ```bash
   python init_users.py
   ```
   默认创建：
   - 管理员: `admin` / `admin123`
   - 测试用户: `test` / `test123`

3. **扫描数据资产**
   - 访问"数据资产"页面
   - 点击"扫描资产"按钮

4. **创建跨境场景**
   - 访问"跨境场景"页面
   - 创建新的传输场景

5. **执行风险评估**
   - 访问"风险评估"页面
   - 创建评估并执行计算

## 常见问题

### 数据库连接失败

确保PostgreSQL已启动，并检查 `backend/app/core/config.py` 中的数据库配置。

### 端口被占用

修改端口：
- 后端: `uvicorn app.main:app --reload --port 8001`
- 前端: 修改 `frontend/vite.config.ts` 中的端口配置

### 依赖安装失败

- Python: 使用国内镜像 `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- Node.js: 使用国内镜像 `npm install --registry=https://registry.npmmirror.com`

## 下一步

- 阅读 [README.md](README.md) 了解系统架构
- 阅读 [DEPLOYMENT.md](DEPLOYMENT.md) 了解部署详情
- 查看 API 文档了解接口使用

## 作者

张彦龙

