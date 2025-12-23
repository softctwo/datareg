"""
API v1 路由
作者：张彦龙
"""
from fastapi import APIRouter
from app.api.v1.endpoints import data_assets, scenarios, risk_assessments, approvals, audit, users, dashboard, auth, roles, export, batch, interception, notifications, system_config

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(data_assets.router, prefix="/data-assets", tags=["数据资产"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["跨境场景"])
api_router.include_router(risk_assessments.router, prefix="/risk-assessments", tags=["风险评估"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["传输审批"])
api_router.include_router(audit.router, prefix="/audit", tags=["审计日志"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(export.router, prefix="/export", tags=["数据导出"])
api_router.include_router(batch.router, prefix="/batch", tags=["批量操作"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["监控仪表盘"])
api_router.include_router(interception.router, prefix="/interception", tags=["拦截与脱敏"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知与提醒"])
api_router.include_router(system_config.router, prefix="/system-config", tags=["系统配置"])

