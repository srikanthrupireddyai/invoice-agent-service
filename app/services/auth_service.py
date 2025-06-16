from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import hashlib
import logging
import json

from app.core.config import get_settings
from app.db.models import IntegrationType, User, UserRole, UserStatus, Tenant
from app.db.repositories.tenant_repository import TenantRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.integration_repository import IntegrationKeyRepository
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserCreate, UserCreateWithCognito, UserUpdate, UserStatusUpdate

# Setup logging
logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication and token management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.encryption_key = self.settings.ENCRYPTION_KEY.encode()
        self.user_repo = UserRepository(db)
        self.tenant_repo = TenantRepository(db)
        self.integration_repo = IntegrationKeyRepository(db)
        
    def _create_cipher(self) -> Fernet:
        """Create Fernet cipher for token encryption/decryption"""
        if not self.encryption_key:
            raise ValueError("Encryption key not configured")
        
        # Ensure the key is 32 bytes for Fernet
        # If key is not 32 bytes, we hash it to get a consistent size
        if len(self.encryption_key) != 32:
            digest = hashlib.sha256(self.encryption_key).digest()
            key = urlsafe_b64encode(digest)
        else:
            key = urlsafe_b64encode(self.encryption_key)
            
        return Fernet(key)
        
    def _encrypt_token(self, token: str) -> str:
        """Encrypt a token"""
        cipher = self._create_cipher()
        return cipher.encrypt(token.encode()).decode()
        
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token"""
        cipher = self._create_cipher()
        return cipher.decrypt(encrypted_token.encode()).decode()
    
    async def create_tenant_with_admin(self, 
                                     tenant_data: TenantCreate, 
                                     user_data: UserCreate,
                                     cognito_id: str) -> Dict[str, Any]:
        """
        Create a new tenant and admin user
        """
        try:
            # Check if tenant with email already exists
            existing_tenant = self.tenant_repo.get_by_email(tenant_data.email)
            if existing_tenant:
                return {"error": "A tenant with this email already exists"}
                
            # Check if user with Cognito ID already exists
            existing_user = self.user_repo.get_by_cognito_id(cognito_id)
            if existing_user:
                return {"error": "User already exists"}
                
            # Create tenant
            tenant = self.tenant_repo.create(tenant_data)
            
            # Create admin user for this tenant
            # Extract user_data dict and remove fields that will be explicitly set
            user_data_dict = user_data.dict()
            # Remove fields that might cause duplication errors
            fields_to_remove = ['cognito_id', 'role', 'status', 'tenant_id']
            for field in fields_to_remove:
                if field in user_data_dict:
                    user_data_dict.pop(field)
                
            user_with_cognito = UserCreateWithCognito(
                **user_data_dict,
                cognito_id=cognito_id,
                tenant_id=tenant.id,
                role=UserRole.ADMIN,
                status=UserStatus.PENDING_CONFIRMATION
            )
            
            user = self.user_repo.create(user_with_cognito)
            
            return {
                "tenant": {
                    "id": tenant.id,
                    "business_name": tenant.business_name,
                    "email": tenant.email
                },
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "status": user.status
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating tenant with admin: {str(e)}")
            return {"error": f"Failed to create tenant: {str(e)}"}
    
    async def add_user_to_tenant(self, 
                               tenant_id: int, 
                               user_data: UserCreate,
                               cognito_id: str) -> Dict[str, Any]:
        """
        Add a new user to an existing tenant
        """
        try:
            # Check if tenant exists
            tenant = self.tenant_repo.get_by_id(tenant_id)
            if not tenant:
                return {"error": "Tenant not found"}
                
            # Check if user with Cognito ID already exists
            existing_user = self.user_repo.get_by_cognito_id(cognito_id)
            if existing_user:
                return {"error": "User already exists"}
                
            # Create user entry in database
            # Extract user_data dict and remove fields that will be explicitly set
            user_data_dict = user_data.dict()
            # Remove fields that might cause duplication errors
            fields_to_remove = ['cognito_id', 'role', 'status', 'tenant_id']
            for field in fields_to_remove:
                if field in user_data_dict:
                    user_data_dict.pop(field)
                
            user_with_cognito = UserCreateWithCognito(
                **user_data_dict,
                cognito_id=cognito_id,
                tenant_id=tenant_id
            )
            
            user = self.user_repo.create(user_with_cognito)
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "status": user.status
                }
            }
            
        except Exception as e:
            logger.error(f"Error adding user to tenant: {str(e)}")
            return {"error": f"Failed to add user: {str(e)}"}
    
    async def store_integration_tokens(self,
                                     tenant_id: int,
                                     integration_type: IntegrationType,
                                     token_data: Dict[str, Any],
                                     expires_at: datetime,
                                     org_id: Optional[str] = None,
                                     tenant_id_external: Optional[str] = None) -> Dict[str, Any]:
        """
        Store encrypted integration tokens for a tenant
        """
        try:
            # Extract tokens
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            if not access_token or not refresh_token:
                return {"error": "Missing required tokens"}
                
            # Encrypt tokens
            encrypted_access = self._encrypt_token(access_token)
            encrypted_refresh = self._encrypt_token(refresh_token)
            
            # Extract and store any additional data
            additional_data = {}
            for key, value in token_data.items():
                if key not in ["access_token", "refresh_token"]:
                    additional_data[key] = value
                    
            additional_json = json.dumps(additional_data) if additional_data else None
                    
            # Store or update integration key
            integration_key = self.integration_repo.create_or_update(
                tenant_id=tenant_id,
                integration_type=integration_type,
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                org_id=org_id,
                tenant_id_external=tenant_id_external,
                additional_data=additional_json
            )
            
            return {
                "success": True,
                "tenant_id": tenant_id,
                "integration_type": integration_key.integration_type,
                "expires_at": integration_key.expires_at
            }
            
        except Exception as e:
            logger.error(f"Error storing integration tokens: {str(e)}")
            return {"error": f"Failed to store integration tokens: {str(e)}"}
    
    async def get_integration_tokens(self,
                                  tenant_id: int,
                                  integration_type: IntegrationType) -> Union[Dict[str, Any], None]:
        """
        Get decrypted integration tokens for a tenant
        """
        try:
            # Retrieve integration key
            integration_key = self.integration_repo.get_by_tenant_and_type(
                tenant_id, integration_type
            )
            
            if not integration_key:
                return None
                
            # Check if token is expired
            now = datetime.utcnow()
            if now >= integration_key.expires_at:
                return {
                    "error": "Token expired",
                    "refresh_token": self._decrypt_token(integration_key.refresh_token),
                    "expires_at": integration_key.expires_at
                }
            
            # Decrypt tokens
            access_token = self._decrypt_token(integration_key.access_token)
            refresh_token = self._decrypt_token(integration_key.refresh_token)
            
            result = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": integration_key.expires_at,
                "org_id": integration_key.org_id,
                "tenant_id_external": integration_key.tenant_id_external
            }
            
            # Add additional data if available
            if integration_key.additional_data:
                additional = json.loads(integration_key.additional_data)
                result.update(additional)
                
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving integration tokens: {str(e)}")
            return {"error": f"Failed to retrieve integration tokens: {str(e)}"}

    async def update_user(self, user_id: int, update_data: UserUpdate) -> Dict[str, Any]:
        """
        Update user data
        """
        try:
            user = self.user_repo.update(user_id, update_data)
            if not user:
                return {"error": "User not found"}
                
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "status": user.status
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return {"error": f"Failed to update user: {str(e)}"}

    async def update_user_status_by_cognito_id(self, cognito_id: str, status_update: UserStatusUpdate) -> Dict[str, Any]:
        """
        Update user status by cognito_id
        This is primarily used for updating a user's status from pending_confirmation to active
        after they confirm their email address.
        """
        try:
            user = self.user_repo.update_status_by_cognito_id(cognito_id, status_update)
            if not user:
                return {"error": "User not found with the provided cognito_id"}
                
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "status": user.status,
                    "tenant_id": user.tenant_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating user status by cognito_id: {str(e)}")
            return {"error": f"Failed to update user status: {str(e)}"}
