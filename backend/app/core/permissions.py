"""
权限验证工具
作者：张彦龙
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.services.role_service import RoleService
from app.services.user_service import UserService
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False  # 不自动抛出错误，让我们手动处理
)


def get_current_user_id(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> int:
    """获取当前用户ID"""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )
    
    return user.id


def require_permission(permission: str):
    """权限验证装饰器/依赖项"""
    def permission_checker(
        user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> int:
        role_service = RoleService(db)
        if not role_service.has_permission(user_id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {permission} 权限"
            )
        return user_id
    
    return permission_checker


def get_current_user_permissions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> list:
    """获取当前用户权限列表"""
    role_service = RoleService(db)
    return role_service.get_user_permissions(user_id)

