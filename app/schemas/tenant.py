from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class BusinessType(str, Enum):
    SOLE_PROPRIETOR = "sole_proprietor"
    LLC = "llc"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class TenantCreate(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    business_type: BusinessType
    email: EmailStr
    estimated_invoices_monthly: Optional[int] = None


class TenantResponse(BaseModel):
    id: str
    business_name: str
    business_type: BusinessType
    email: EmailStr
    estimated_invoices_monthly: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
