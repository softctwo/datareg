"""
用户服务
作者：张彦龙
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户详情"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        hashed_password = pwd_context.hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """更新用户"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        if user_data.get("email") is not None:
            user.email = user_data["email"]
        if user_data.get("full_name") is not None:
            user.full_name = user_data["full_name"]
        if user_data.get("password"):
            user.hashed_password = pwd_context.hash(user_data["password"])
        if user_data.get("is_active") is not None:
            user.is_active = user_data["is_active"]
        if user_data.get("is_superuser") is not None:
            user.is_superuser = user_data["is_superuser"]
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # 不能删除自己
        # 这里可以添加更多业务逻辑
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def get_total_count(self) -> int:
        """获取用户总数"""
        return self.db.query(User).count()

