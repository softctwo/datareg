# 银行重要数据跨境数据管控系统 - 项目概览

## 项目基本信息

**项目名称**: 银行重要数据跨境数据管控系统
**作者**: 张彦龙
**项目类型**: 金融科技合规平台
**开发语言**: Python 3.11+, TypeScript
**许可证**: 内部使用

## 项目目标

构建一个面向银行的跨境数据传输合规管控平台，实现数据资产识别、跨境场景管理、风险评估、事中拦截与动态脱敏、监控审计等全流程功能，确保数据出境符合《数据安全法》、《个人信息保护法》和《数据出境安全评估办法》的合规要求。

## 技术栈

### 后端技术栈
- **框架**: FastAPI 0.104.1
- **数据库ORM**: SQLAlchemy 2.0.23
- **数据库**: PostgreSQL 14+
- **数据库迁移**: Alembic 1.12.1
- **认证**: JWT (python-jose)
- **密码加密**: Passlib with Bcrypt
- **异步任务**: Celery 5.3.4 + Redis 5.0.1
- **数据处理**: Pandas 2.1.3 + NumPy 1.26.2

### 前端技术栈
- **框架**: React 18.2.0
- **语言**: TypeScript 5.3.3
- **路由**: React Router DOM 6.20.0
- **UI库**: Ant Design 5.12.0
- **图标**: Ant Design Icons 5.2.6
- **HTTP客户端**: Axios 1.6.2
- **时间处理**: Day.js 1.11.10
- **图表**: ECharts 5.4.3 + echarts-for-react 3.0.2
- **构建工具**: Vite 5.0.8

### 开发工具
- **API文档**: 自动生成Swagger/OpenAPI
- **类型检查**: Python类型提示 + TypeScript
- **代码格式化**: 预留配置

## 项目架构

### 后端架构 (MVC模式)
```
backend/app/
├── api/v1/endpoints/    # API路由层
│   ├── auth.py         # 认证相关
│   ├── data_assets.py  # 数据资产管理
│   ├── scenarios.py    # 跨境场景管理
│   ├── risk_assessments.py # 风险评估
│   ├── approvals.py    # 传输审批
│   ├── audit.py        # 审计日志
│   ├── dashboard.py    # 仪表盘
│   ├── users.py        # 用户管理
│   ├── roles.py        # 角色管理
│   ├── batch.py        # 批量操作
│   └── export.py       # 数据导出
├── core/               # 核心配置
│   ├── config.py       # 配置管理
│   ├── database.py     # 数据库连接
│   ├── security.py     # 安全相关
│   └── permissions.py  # 权限管理
├── models/             # 数据模型层
│   ├── data_asset.py   # 数据资产模型
│   ├── scenario.py     # 场景模型
│   ├── risk.py         # 风险评估模型
│   ├── approval.py     # 审批模型
│   ├── audit.py        # 审计模型
│   ├── user.py         # 用户模型
│   └── role.py         # 角色模型
├── schemas/            # Pydantic模式
├── services/           # 业务逻辑层
│   ├── data_asset_service.py
│   ├── scenario_service.py
│   ├── risk_service.py
│   ├── approval_service.py
│   ├── audit_service.py
│   ├── user_service.py
│   ├── role_service.py
│   ├── dashboard_service.py
│   └── interception_service.py
└── utils/              # 工具函数
    ├── data_scanner.py      # 数据扫描
    ├── desensitization.py  # 数据脱敏
    ├── classification_engine.py # 分类引擎
    └── export.py          # 数据导出
```

### 前端架构
```
frontend/src/
├── components/         # 通用组件
├── pages/             # 页面组件
│   ├── Login.tsx      # 登录页
│   ├── Dashboard.tsx  # 仪表盘
│   ├── DataAssets.tsx # 数据资产
│   ├── Scenarios.tsx  # 跨境场景
│   ├── RiskAssessments.tsx # 风险评估
│   ├── Approvals.tsx  # 传输审批
│   ├── AuditLogs.tsx  # 审计日志
│   ├── Roles.tsx      # 角色管理
│   ├── UserRoles.tsx  # 用户角色
│   └── Users.tsx      # 用户管理
├── services/          # API服务
└── utils/             # 工具函数
```

## 核心功能模块

### 1. 数据资产分类分级 ✅
- 自动扫描PostgreSQL数据库表
- 敏感标签定义和管理
- 重要数据自动识别
- 数据安全级别分类（核心/重要/敏感/个人/内部/公开）
- 数据血缘追踪

### 2. 跨境传输场景管理 ✅
- 业务场景备案
- 传输要素管理
- 场景状态管理（草稿/待审批/已批准/已拒绝/已过期/已暂停）
- 场景审批流程

### 3. 数据出境风险自评估引擎 ✅
- PIA/DPIA评估模板
- 多维度评估
- 阈值检查（100万个人信息/10万敏感个人信息）
- 接近阈值预警（95%阈值预警）
- 综合风险等级计算

### 4. 事中拦截与动态脱敏 ✅
- 白名单策略
- 黑名单策略
- 核心数据拦截
- 动态脱敏引擎（身份证、手机号、银行卡、姓名、邮箱）

### 5. 传输审批模块 ✅
- 传输审批申请创建
- 审批状态管理
- 审批流程
- 传输记录

### 6. 监控与审计仪表盘 ✅
- 概览统计
- 传输趋势分析
- 目的国分布统计
- 风险预警展示
- 审计日志记录
- 异常行为检测

### 7. 用户认证和权限管理 ✅
- JWT Token认证
- 角色权限管理
- 路由守卫

### 8. 批量操作和数据导出 ✅
- 批量审批、拒绝、删除
- CSV/JSON格式导出

## 合规特性

- 支持《数据安全法》要求
- 支持《个人信息保护法》要求
- 支持《数据出境安全评估办法》要求
- 阈值预警机制
- 风险评估模板
- 审计日志完整记录

## 数据库设计要点

### 核心表结构
- users/roles: 用户角色管理
- data_assets: 数据资产
- data_classifications: 数据分类
- sensitive_tags: 敏感标签
- scenarios: 跨境场景
- approvals: 传输审批
- risk_assessments: 风险评估
- audit_logs: 审计日志

### 关键特性
- 支持数据血缘关系
- 标签系统支持多对多关系
- 审计日志记录所有操作
- 软删除支持

## 环境配置

### 开发环境
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### 生产环境考虑
- 负载均衡
- 数据库主从复制
- Redis集群
- 容器化部署

## 安全措施

- JWT Token认证
- 密码Bcrypt加密
- SQL注入防护
- CORS配置
- 权限验证
- 审计日志
- 数据脱敏

## 性能优化

- 数据库索引优化
- 异步任务处理
- 分页查询
- 缓存策略（预留Redis集成）