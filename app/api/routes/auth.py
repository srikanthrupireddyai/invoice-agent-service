from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, check_admin_role
from app.db.models import User
from app.db.session import get_db
from app.schemas.tenant import TenantCreate, TenantResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate, CurrentUser
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=dict)
async def signup_tenant(
    tenant_data: TenantCreate,
    user_data: UserCreate,
    cognito_id: str,
    db: Session = Depends(get_db)
):
    """
    Register a new tenant and admin user after Cognito signup.
    This endpoint is called after the user has signed up with Cognito.
    """
    auth_service = AuthService(db)
    result = await auth_service.create_tenant_with_admin(
        tenant_data=tenant_data,
        user_data=user_data,
        cognito_id=cognito_id
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result


@router.post("/users", response_model=dict)
async def add_user(
    user_data: UserCreate,
    cognito_id: str,
    current_user: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Add a new user to the current tenant.
    Only administrators can add new users.
    """
    auth_service = AuthService(db)
    result = await auth_service.add_user_to_tenant(
        tenant_id=current_user.tenant_id,
        user_data=user_data,
        cognito_id=cognito_id
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result


@router.get("/me", response_model=CurrentUser)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user
    """
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def list_tenant_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all users in the current tenant
    """
    from app.db.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    users = user_repo.get_by_tenant(
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit
    )
    return users


@router.patch("/users/{user_id}", response_model=dict)
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """
    Update user information.
    Only administrators can update user information.
    """
    # Check if user belongs to the same tenant as admin
    from app.db.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    auth_service = AuthService(db)
    result = await auth_service.update_user(user_id, user_update)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
        
    return result
