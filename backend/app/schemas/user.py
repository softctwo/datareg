"""
用户Schema
作者：张彦龙
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str


class UserUpdate(BaseModel):
    """更新用户"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    is_superuser: bool
    roles: Optional[List[dict]] = Field(None, description="角色列表")
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

