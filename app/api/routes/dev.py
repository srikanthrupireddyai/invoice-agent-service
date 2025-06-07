"""
Development and testing utility endpoints
These endpoints are only enabled in development mode
"""
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import BusinessType, Tenant, User, UserRole, UserStatus
from app.db.repositories.tenant_repository import TenantRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db
from app.schemas.tenant import TenantCreate, TenantResponse
from app.schemas.user import UserResponse

settings = get_settings()

# Only create router if in development mode
router = APIRouter()

@router.get("/check", response_model=Dict)
async def check_dev_mode():
    """
    Check if development mode is enabled and auth is disabled
    """
    return {
        "dev_mode": settings.APP_ENV == "development",
        "auth_disabled": not settings.AUTH_ENABLED,
        "app_env": settings.APP_ENV
    }

@router.post("/create-test-tenant", response_model=Dict)
async def create_test_tenant(
    business_name: str = "Test Company",
    email: str = "test@example.com",
    business_type: BusinessType = BusinessType.LLC, 
    db: Session = Depends(get_db)
):
    """
    Create a test tenant with an admin user
    Only available when AUTH_ENABLED is False
    """
    if settings.AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available when AUTH_ENABLED is False"
        )
    
    try:
        # Create tenant
        tenant = Tenant(
            business_name=business_name,
            business_type=business_type,
            email=email,
            estimated_invoices_monthly=100
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        # Create admin user
        user = User(
            email=email,
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            cognito_id=f"dev-{uuid.uuid4()}",
            tenant_id=tenant.id
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "success": True,
            "message": "Test tenant and admin user created",
            "tenant": {
                "id": tenant.id,
                "business_name": tenant.business_name,
                "email": tenant.email
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "tenant_id": user.tenant_id,
                "role": user.role.value
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test tenant: {str(e)}"
        )

@router.get("/tenants", response_model=List[TenantResponse])
async def list_all_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all tenants in the system
    Only available when AUTH_ENABLED is False
    """
    if settings.AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available when AUTH_ENABLED is False"
        )
    
    tenant_repo = TenantRepository(db)
    return tenant_repo.get_all(skip=skip, limit=limit)

@router.get("/tenants/{tenant_id}/users", response_model=List[UserResponse])
async def list_tenant_users(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """
    List all users for a specific tenant
    Only available when AUTH_ENABLED is False
    """
    if settings.AUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available when AUTH_ENABLED is False"
        )
    
    # Verify tenant exists
    tenant_repo = TenantRepository(db)
    tenant = tenant_repo.get_by_id(tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Get users for the tenant
    user_repo = UserRepository(db)
    return user_repo.get_by_tenant(tenant_id=tenant_id)
