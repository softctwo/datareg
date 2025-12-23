# 银行重要数据跨境数据管控系统

## 项目简介

本系统是面向银行的跨境数据传输合规管控平台，实现数据资产识别、跨境场景管理、风险评估、事中拦截与动态脱敏、监控审计等全流程功能。

## 核心功能

✅ **数据资产分类分级** - 自动扫描、敏感数据识别、重要数据标记  
✅ **跨境传输场景管理** - 场景备案、审批流程、状态管理、批量操作  
✅ **风险评估引擎** - PIA/DPIA评估、阈值预警、风险等级计算  
✅ **拦截与脱敏** - 黑白名单、动态脱敏、核心数据拦截  
✅ **传输审批** - 审批申请、流程管理、状态跟踪、批量审批  
✅ **监控审计** - 流量监控、异常检测、审计日志  
✅ **用户认证** - JWT Token认证、路由守卫、安全保护  
✅ **角色权限管理** - 角色CRUD、权限分配、权限验证  
✅ **数据导出** - CSV/JSON格式导出、多模块支持  
✅ **批量操作** - 批量审批、批量拒绝、批量删除

## 技术栈

- **后端：** FastAPI + Python 3.11+
- **前端：** React 18 + TypeScript + Ant Design
- **数据库：** PostgreSQL 14+
- **认证：** JWT

## 项目结构

```
datareg/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── alembic/         # 数据库迁移
│   └── requirements.txt
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── services/    # API服务
│   │   └── utils/       # 工具
│   └── package.json
└── docs/                # 文档
```

## 快速开始

### 方式一：一键启动（推荐）

```bash
# 给启动脚本添加执行权限（首次使用）
chmod +x start.sh

# 启动系统
./start.sh
```

启动脚本会自动：
- 检查数据库连接
- 启动后端服务（端口8000）
- 启动前端服务（端口3000）
- 显示访问地址和登录信息

### 方式二：手动启动

#### 1. 初始化数据库

```bash
cd backend
python3 create_db.py      # 创建数据库（如果不存在）
python3 init_db.py         # 初始化表结构
python3 init_users.py      # 创建默认用户
python3 init_demo_data.py  # 创建演示数据（可选）
```

#### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 默认用户

系统初始化后会自动创建以下用户：
- **管理员**: `admin` / `admin123`
- **测试用户**: `test` / `test123`

### 访问系统

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs

### 数据库配置

默认配置（可在 `backend/app/core/config.py` 中修改）：
- 用户: `postgres`
- 密码: `3f342bb206`
- 数据库: `datareg`

## 作者

张彦龙

