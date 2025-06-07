from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_CONFIRMATION = "pending_confirmation"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING_CONFIRMATION


class UserCreateWithCognito(UserCreate):
    cognito_id: str
    tenant_id: str
    

class UserResponse(UserBase):
    id: int
    cognito_id: str
    tenant_id: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    
    
class CurrentUser(UserBase):
    tenant_id: str
    role: UserRole
    status: UserStatus
    
    class Config:
        from_attributes = True
