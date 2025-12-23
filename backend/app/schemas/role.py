"""
角色Schema
作者：张彦龙
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="描述")
    permissions: Optional[List[str]] = Field(None, description="权限列表")


class RoleCreate(RoleBase):
    """创建角色"""
    pass


class RoleUpdate(BaseModel):
    """更新角色"""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    """用户角色分配"""
    user_id: int
    role_ids: List[int]

