from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import IntegrationKey, IntegrationType


class IntegrationKeyRepository:
    """
    Repository class for handling database operations related to IntegrationKey model
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_integration_key(
        self,
        user_id: int,
        integration_type: IntegrationType,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
        org_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        additional_data: Optional[str] = None
    ) -> IntegrationKey:
        """
        Create a new integration key entry
        """
        key = IntegrationKey(
            user_id=user_id,
            integration_type=integration_type,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            org_id=org_id,
            tenant_id=tenant_id,
            additional_data=additional_data
        )
        self.db.add(key)
        self.db.commit()
        self.db.refresh(key)
        return key
    
    def get_integration_key_by_user_and_type(
        self, 
        user_id: int, 
        integration_type: IntegrationType
    ) -> Optional[IntegrationKey]:
        """
        Get integration keys for a specific user and integration type
        """
        return self.db.query(IntegrationKey).filter(
            IntegrationKey.user_id == user_id,
            IntegrationKey.integration_type == integration_type
        ).first()
    
    def update_integration_key(
        self, 
        key_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[IntegrationKey]:
        """
        Update an existing integration key
        """
        key = self.db.query(IntegrationKey).filter(IntegrationKey.id == key_id).first()
        if not key:
            return None
        
        for field, value in update_data.items():
            setattr(key, field, value)
        
        self.db.commit()
        self.db.refresh(key)
        return key
