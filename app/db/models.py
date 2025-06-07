from datetime import datetime
from enum import Enum
import uuid
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Enum as SQLAEnum
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Import Base from session
from app.db.session import Base


class IntegrationType(str, Enum):
    ZOHO = "zoho"
    QUICKBOOKS = "quickbooks"
    XERO = "xero"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_CONFIRMATION = "pending_confirmation"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class BusinessType(str, Enum):
    SOLE_PROPRIETOR = "sole_proprietor"
    LLC = "llc"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    OTHER = "other"


def generate_uuid():
    """Generate a UUID string for database IDs"""
    return str(uuid.uuid4())


class Tenant(Base):
    """
    Tenant model representing a business entity
    """
    __tablename__ = "tenants"

    id = Column(VARCHAR(36), primary_key=True, default=generate_uuid)
    business_name = Column(String(255), nullable=False)
    business_type = Column(SQLAEnum(BusinessType), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    estimated_invoices_monthly = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="tenant")
    integration_keys = relationship("IntegrationKey", back_populates="tenant")


class User(Base):
    """
    User model for authentication and authorization
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(VARCHAR(36), ForeignKey("tenants.id"), nullable=False)
    cognito_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(SQLAEnum(UserRole), nullable=False, default=UserRole.USER)
    status = Column(SQLAEnum(UserStatus), nullable=False, default=UserStatus.PENDING_CONFIRMATION)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="users")


class IntegrationKey(Base):
    """
    Model for storing encrypted integration keys (access tokens, refresh tokens)
    """
    __tablename__ = "integration_keys"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(VARCHAR(36), ForeignKey("tenants.id"), nullable=False)
    integration_type = Column(SQLAEnum(IntegrationType), nullable=False)
    
    # Encrypted tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    
    # Additional information
    expires_at = Column(DateTime(timezone=True), nullable=False)
    org_id = Column(String(255), nullable=True)
    tenant_id_external = Column(String(255), nullable=True)
    additional_data = Column(Text, nullable=True)  # Store as JSON string if needed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="integration_keys")
