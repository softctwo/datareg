# 银行重要数据跨境数据管控系统 - 后端

## 项目结构

```
backend/
├── app/
│   ├── api/              # API路由
│   │   └── v1/
│   │       └── endpoints/ # 各个模块的端点
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   └── database.py   # 数据库连接
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # 业务逻辑层
│   ├── utils/            # 工具函数
│   └── main.py           # 应用入口
├── alembic/              # 数据库迁移
├── requirements.txt      # Python依赖
└── init_db.py           # 数据库初始化脚本
```

## 核心模块

### 1. 数据资产分类分级
- 元数据自动扫描
- 敏感数据识别
- 重要数据标记
- 数据血缘追踪

### 2. 跨境传输场景管理
- 场景备案
- 传输要素管理
- 审批流程

### 3. 风险评估引擎
- PIA/DPIA评估
- 阈值预警
- 风险等级计算

### 4. 拦截与脱敏
- 黑白名单策略
- 动态脱敏
- 核心数据拦截

### 5. 监控与审计
- 流量监控
- 异常检测
- 审计日志

## API文档

启动服务后访问：`http://localhost:8000/api/docs`

## 开发指南

### 添加新API端点

1. 在 `app/api/v1/endpoints/` 创建新的端点文件
2. 在 `app/api/v1/__init__.py` 注册路由
3. 创建对应的Schema和Service

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 作者

张彦龙

