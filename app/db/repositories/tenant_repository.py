from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import Tenant, generate_uuid
from app.schemas.tenant import TenantCreate


class TenantRepository:
    """
    Repository for Tenant CRUD operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, tenant_data: TenantCreate) -> Tenant:
        """
        Create a new tenant
        """
        db_tenant = Tenant(
            business_name=tenant_data.business_name,
            business_type=tenant_data.business_type,
            email=tenant_data.email,
            estimated_invoices_monthly=tenant_data.estimated_invoices_monthly
        )
        
        self.db.add(db_tenant)
        self.db.commit()
        self.db.refresh(db_tenant)
        
        return db_tenant
        
    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID
        """
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
    def get_by_email(self, email: str) -> Optional[Tenant]:
        """
        Get tenant by email
        """
        return self.db.query(Tenant).filter(Tenant.email == email).first()
        
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """
        Get all tenants
        """
        return self.db.query(Tenant).offset(skip).limit(limit).all()
        
    def update(self, tenant_id: str, update_data: Dict[str, Any]) -> Optional[Tenant]:
        """
        Update tenant by ID
        """
        tenant = self.get_by_id(tenant_id)
        if not tenant:
            return None
            
        for key, value in update_data.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
                
        self.db.commit()
        self.db.refresh(tenant)
        
        return tenant
        
    def delete(self, tenant_id: str) -> bool:
        """
        Delete tenant by ID
        """
        tenant = self.get_by_id(tenant_id)
        if not tenant:
            return False
            
        self.db.delete(tenant)
        self.db.commit()
        
        return True
