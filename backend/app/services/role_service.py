"""
角色服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.models.user import Role, User
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    """角色服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_roles(self) -> List[Role]:
        """获取角色列表"""
        return self.db.query(Role).all()
    
    def get_role(self, role_id: int) -> Optional[Role]:
        """获取角色详情"""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def create_role(self, role_data: RoleCreate) -> Role:
        """创建角色"""
        permissions_json = json.dumps(role_data.permissions or [])
        db_role = Role(
            name=role_data.name,
            description=role_data.description,
            permissions=permissions_json
        )
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role
    
    def update_role(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        db_role = self.get_role(role_id)
        if not db_role:
            return None
        
        if role_data.name:
            db_role.name = role_data.name
        if role_data.description is not None:
            db_role.description = role_data.description
        if role_data.permissions is not None:
            db_role.permissions = json.dumps(role_data.permissions)
        
        self.db.commit()
        self.db.refresh(db_role)
        return db_role
    
    def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        db_role = self.get_role(role_id)
        if not db_role:
            return False
        
        self.db.delete(db_role)
        self.db.commit()
        return True
    
    def assign_roles_to_user(self, user_id: int, role_ids: List[int]) -> Optional[User]:
        """为用户分配角色"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 获取角色
        roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all()
        user.roles = roles
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户所有权限"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # 如果是超级用户，返回所有权限
        if user.is_superuser:
            return ["*"]  # 所有权限
        
        # 收集所有角色的权限
        all_permissions = set()
        for role in user.roles:
            if role.permissions:
                try:
                    permissions = json.loads(role.permissions)
                    all_permissions.update(permissions)
                except:
                    pass
        
        return list(all_permissions)
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """检查用户是否有指定权限"""
        permissions = self.get_user_permissions(user_id)
        return "*" in permissions or permission in permissions

