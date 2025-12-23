"""
银行重要数据跨境数据管控系统 - 主应用入口
作者：张彦龙
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title="银行重要数据跨境数据管控系统",
    description="跨境数据传输合规管控平台",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
    # 注意：redirect_slashes默认为True，但FastAPI会正确处理带/不带斜杠的路由
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "银行重要数据跨境数据管控系统 API",
        "version": "1.0.0",
        "author": "张彦龙"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

