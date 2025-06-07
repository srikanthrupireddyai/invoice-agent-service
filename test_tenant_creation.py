"""
Test script to verify tenant and user creation with UUID tenant IDs
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import generate_uuid, Tenant, User, BusinessType, UserRole, UserStatus
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserCreateWithCognito
from app.db.repositories.tenant_repository import TenantRepository
from app.db.repositories.user_repository import UserRepository

def test_tenant_user_creation():
    # Create database session
    db = SessionLocal()
    try:
        # Create tenant repository
        tenant_repo = TenantRepository(db)
        
        # Create a new tenant
        tenant_data = TenantCreate(
            business_name="Test Business",
            business_type=BusinessType.LLC,
            email="test@example.com",
            estimated_invoices_monthly=100
        )
        
        tenant = tenant_repo.create(tenant_data)
        print(f"\n=== Created Tenant ===")
        print(f"ID (UUID): {tenant.id}")
        print(f"Business Name: {tenant.business_name}")
        print(f"Business Type: {tenant.business_type}")
        print(f"Email: {tenant.email}")
        print(f"Created At: {tenant.created_at}")
        
        # Verify UUID format
        print(f"\nVerifying UUID format: {len(tenant.id) == 36}")
        
        # Create user repository
        user_repo = UserRepository(db)
        
        # Create a new admin user for the tenant
        user_data = UserCreateWithCognito(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            cognito_id="test-cognito-id-123",
            tenant_id=tenant.id  # Using the UUID tenant ID
        )
        
        user = user_repo.create(user_data)
        print(f"\n=== Created User ===")
        print(f"ID: {user.id}")
        print(f"Tenant ID: {user.tenant_id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Status: {user.status}")
        
        # Verify tenant ID matches between user and tenant
        print(f"\nVerifying tenant ID link: {user.tenant_id == tenant.id}")
        
        # Verify retrieving user by tenant ID works
        users_by_tenant = user_repo.get_by_tenant(tenant.id)
        print(f"\nUsers found for tenant: {len(users_by_tenant)}")
    finally:
        db.close()
        
if __name__ == "__main__":
    test_tenant_user_creation()
