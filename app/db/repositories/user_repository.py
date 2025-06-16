from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas.user import UserCreate, UserCreateWithCognito, UserUpdate, UserStatusUpdate


class UserRepository:
    """
    Repository for User CRUD operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, user_data: UserCreateWithCognito) -> User:
        """
        Create a new user
        """
        db_user = User(
            cognito_id=user_data.cognito_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            tenant_id=user_data.tenant_id,
            role=user_data.role,
            status=user_data.status
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
        
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        """
        return self.db.query(User).filter(User.id == user_id).first()
        
    def get_by_cognito_id(self, cognito_id: str) -> Optional[User]:
        """
        Get user by Cognito ID
        """
        return self.db.query(User).filter(User.cognito_id == cognito_id).first()
        
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users for a specific tenant
        """
        return self.db.query(User).filter(User.tenant_id == tenant_id).offset(skip).limit(limit).all()
        
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users
        """
        return self.db.query(User).offset(skip).limit(limit).all()
        
    def update(self, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """
        Update user by ID
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
            
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
                
        self.db.commit()
        self.db.refresh(user)
        
        return user
        
    def update_by_cognito_id(self, cognito_id: str, update_data: UserUpdate) -> Optional[User]:
        """
        Update user by Cognito ID
        """
        user = self.get_by_cognito_id(cognito_id)
        if not user:
            return None
            
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
                
        self.db.commit()
        self.db.refresh(user)
        
        return user
        
    def update_status_by_cognito_id(self, cognito_id: str, status_update: UserStatusUpdate) -> Optional[User]:
        """
        Update user status by Cognito ID
        This focused method only updates the status field for security reasons
        """
        user = self.get_by_cognito_id(cognito_id)
        if not user:
            return None
            
        user.status = status_update.status
        self.db.commit()
        self.db.refresh(user)
        
        return user
        
    def delete(self, user_id: int) -> bool:
        """
        Delete user by ID
        """
        user = self.get_by_id(user_id)
        if not user:
            return False
            
        self.db.delete(user)
        self.db.commit()
        
        return True
