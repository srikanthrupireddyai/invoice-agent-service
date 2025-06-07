"""
Simple test script to verify UUID generation and model relationships
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.models import generate_uuid, Tenant, User, BusinessType, UserRole, UserStatus

def test_uuid_models():
    # Create database session
    db = SessionLocal()
    try:
        # Create a new tenant with UUID
        tenant = Tenant(
            business_name="Test Business",
            business_type=BusinessType.LLC,
            email="test@example.com",
            estimated_invoices_monthly=100
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        print(f"\n=== Created Tenant ===")
        print(f"ID (UUID): {tenant.id}")
        print(f"Business Name: {tenant.business_name}")
        print(f"Business Type: {tenant.business_type}")
        print(f"Email: {tenant.email}")
        print(f"Created At: {tenant.created_at}")
        
        # Verify UUID format
        print(f"\nVerifying UUID format: {len(tenant.id) == 36}")
        
        # Create a new admin user for the tenant
        user = User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            cognito_id="test-cognito-id-123",
            tenant_id=tenant.id  # Using the UUID tenant ID
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"\n=== Created User ===")
        print(f"ID: {user.id}")
        print(f"Tenant ID: {user.tenant_id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Status: {user.status}")
        
        # Verify tenant ID matches between user and tenant
        print(f"\nVerifying tenant ID link: {user.tenant_id == tenant.id}")
        
        # Query to verify relationship works
        test_user = db.query(User).filter(User.id == user.id).first()
        print(f"\nVerifying tenant relationship: {test_user.tenant.business_name == tenant.business_name}")
        
    finally:
        # Clean up - remove test data
        if 'user' in locals():
            db.delete(user)
        if 'tenant' in locals():
            db.delete(tenant)
        db.commit()
        db.close()
        
if __name__ == "__main__":
    test_uuid_models()
