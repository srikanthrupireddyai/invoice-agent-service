from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class IntegrationType(str, Enum):
    """Enum for integration types in API requests"""
    ZOHO = "zoho"
    QUICKBOOKS = "quickbooks"
    XERO = "xero"


class AuthCodeRequest(BaseModel):
    """
    Schema for authorization code exchange request
    """
    auth_code: str = Field(..., description="Authorization code received from OAuth provider")
    user_id: int = Field(..., description="User ID to associate with this integration")
    integration_type: IntegrationType = Field(..., description="Type of accounting integration")
    org_id: Optional[str] = Field(None, description="Organization ID if applicable")
    tenant_id: Optional[str] = Field(None, description="Tenant ID if applicable")


class RefreshTokenRequest(BaseModel):
    """
    Schema for token refresh request
    """
    user_id: int = Field(..., description="User ID associated with the integration")
    integration_type: IntegrationType = Field(..., description="Type of accounting integration")


class AuthResponse(BaseModel):
    """
    Schema for authentication response
    """
    status: str
    message: str
    integration_type: str
    expires_at: str


class ErrorResponse(BaseModel):
    """
    Schema for error responses
    """
    detail: str
