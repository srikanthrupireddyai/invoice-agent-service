from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import IntegrationKey, IntegrationType


class IntegrationKeyRepository:
    """
    Repository for IntegrationKey CRUD operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, 
               tenant_id: str, 
               integration_type: IntegrationType,
               access_token: str,
               refresh_token: str,
               expires_at: datetime,
               org_id: Optional[str] = None,
               tenant_id_external: Optional[str] = None,
               additional_data: Optional[str] = None
            ) -> IntegrationKey:
        """
        Create a new integration key for a tenant
        """
        # Check if integration key already exists for this tenant and integration type
        existing_key = self.get_by_tenant_and_type(tenant_id, integration_type)
        
        # If key exists, update it instead of creating a new one
        if existing_key:
            existing_key.access_token = access_token
            existing_key.refresh_token = refresh_token
            existing_key.expires_at = expires_at
            existing_key.org_id = org_id
            existing_key.tenant_id_external = tenant_id_external
            existing_key.additional_data = additional_data
            existing_key.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(existing_key)
            return existing_key
            
        # Create new integration key
        db_key = IntegrationKey(
            tenant_id=tenant_id,
            integration_type=integration_type,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            org_id=org_id,
            tenant_id_external=tenant_id_external,
            additional_data=additional_data
        )
        
        self.db.add(db_key)
        self.db.commit()
        self.db.refresh(db_key)
        
        return db_key
        
    def get_by_id(self, key_id: int) -> Optional[IntegrationKey]:
        """
        Get integration key by ID
        """
        return self.db.query(IntegrationKey).filter(IntegrationKey.id == key_id).first()
        
    def get_by_tenant_and_type(self, tenant_id: str, integration_type: IntegrationType) -> Optional[IntegrationKey]:
        """
        Get integration key by tenant ID and integration type
        """
        return self.db.query(IntegrationKey).filter(
            IntegrationKey.tenant_id == tenant_id,
            IntegrationKey.integration_type == integration_type
        ).first()
        
    def get_all_by_tenant(self, tenant_id: str) -> List[IntegrationKey]:
        """
        Get all integration keys for a tenant
        """
        return self.db.query(IntegrationKey).filter(
            IntegrationKey.tenant_id == tenant_id
        ).all()
        
    def update(self, key_id: int, update_data: Dict[str, Any]) -> Optional[IntegrationKey]:
        """
        Update integration key by ID
        """
        key = self.get_by_id(key_id)
        if not key:
            return None
            
        for field, value in update_data.items():
            if hasattr(key, field):
                setattr(key, field, value)
                
        self.db.commit()
        self.db.refresh(key)
        
        return key
        
    def delete(self, key_id: int) -> bool:
        """
        Delete integration key by ID
        """
        key = self.get_by_id(key_id)
        if not key:
            return False
            
        self.db.delete(key)
        self.db.commit()
        
        return True
        
    def delete_by_tenant_and_type(self, tenant_id: str, integration_type: IntegrationType) -> bool:
        """
        Delete integration key by tenant ID and integration type
        """
        key = self.get_by_tenant_and_type(tenant_id, integration_type)
        if not key:
            return False
            
        self.db.delete(key)
        self.db.commit()
        
        return True
