"""
用户管理API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import exists
from typing import List
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    service = UserService(db)
    users = service.list_users(skip=skip, limit=limit)
    # 添加角色信息
    result = []
    for user in users:
        # 手动构建字典，避免Pydantic验证Role对象
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": [{"id": r.id, "name": r.name} for r in user.roles]
        }
        result.append(UserResponse(**user_dict))
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户详情"""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 手动构建字典，避免Pydantic验证Role对象
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": [{"id": r.id, "name": r.name} for r in user.roles]
    }
    return UserResponse(**user_dict)


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    service = UserService(db)
    # 检查用户名是否已存在
    existing_user = service.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    if user.email:
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已存在")
    
    created_user = service.create_user(user)
    # 返回用户信息（包含角色）
    user_dict = {
        "id": created_user.id,
        "username": created_user.username,
        "email": created_user.email,
        "full_name": created_user.full_name,
        "is_active": created_user.is_active,
        "is_superuser": created_user.is_superuser,
        "created_at": created_user.created_at,
        "updated_at": created_user.updated_at,
        "roles": []
    }
    return UserResponse(**user_dict)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """更新用户"""
    service = UserService(db)
    user_data = user.model_dump(exclude_unset=True)
    updated_user = service.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 返回用户信息（包含角色）
    user_dict = {
        "id": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email,
        "full_name": updated_user.full_name,
        "is_active": updated_user.is_active,
        "is_superuser": updated_user.is_superuser,
        "created_at": updated_user.created_at,
        "updated_at": updated_user.updated_at,
        "roles": [{"id": r.id, "name": r.name} for r in updated_user.roles]
    }
    return UserResponse(**user_dict)


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    service = UserService(db)
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "删除成功"}


@router.get("/stats/count", response_model=dict)
async def get_user_count(db: Session = Depends(get_db)):
    """获取用户统计"""
    service = UserService(db)
    total = service.get_total_count()
    active_count = db.query(User).filter(User.is_active == True).count()
    return {
        "total": total,
        "active": active_count,
        "inactive": total - active_count
    }

