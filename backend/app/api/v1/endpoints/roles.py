"""
角色管理API端点
作者：张彦龙
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, UserRoleAssign
from app.services.role_service import RoleService

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
async def list_roles(db: Session = Depends(get_db)):
    """获取角色列表"""
    service = RoleService(db)
    roles = service.list_roles()
    # 解析permissions JSON
    for role in roles:
        if role.permissions:
            import json
            try:
                role.permissions = json.loads(role.permissions)
            except:
                role.permissions = []
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """获取角色详情"""
    service = RoleService(db)
    role = service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    # 解析permissions JSON
    if role.permissions:
        import json
        try:
            role.permissions = json.loads(role.permissions)
        except:
            role.permissions = []
    return role


@router.post("/", response_model=RoleResponse)
async def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """创建角色"""
    service = RoleService(db)
    return service.create_role(role)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db)):
    """更新角色"""
    service = RoleService(db)
    updated = service.update_role(role_id, role)
    if not updated:
        raise HTTPException(status_code=404, detail="角色不存在")
    # 解析permissions JSON
    if updated.permissions:
        import json
        try:
            updated.permissions = json.loads(updated.permissions)
        except:
            updated.permissions = []
    return updated


@router.delete("/{role_id}")
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    """删除角色"""
    service = RoleService(db)
    success = service.delete_role(role_id)
    if not success:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"message": "删除成功"}


@router.post("/assign", response_model=dict)
async def assign_roles(assignment: UserRoleAssign, db: Session = Depends(get_db)):
    """为用户分配角色"""
    service = RoleService(db)
    user = service.assign_roles_to_user(assignment.user_id, assignment.role_ids)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "角色分配成功", "user_id": user.id}


@router.get("/user/{user_id}/permissions", response_model=List[str])
async def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    """获取用户权限列表"""
    service = RoleService(db)
    return service.get_user_permissions(user_id)

