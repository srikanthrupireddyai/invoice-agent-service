from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class AccountingIntegrationBase(ABC):
    """
    Base abstract class for all accounting system integrations.
    Defines the common interface that all integrations must implement.
    """
    
    @abstractmethod
    async def exchange_auth_code(self, auth_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token and refresh token
        """
        pass
    
    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Use refresh token to get a new access token when current one expires
        """
        pass
    
    @abstractmethod
    async def get_token_expiry(self, token_data: Dict[str, Any]) -> datetime:
        """
        Calculate token expiry datetime from token data
        """
        pass
    
    @abstractmethod
    def get_integration_type(self) -> str:
        """
        Return the type of integration this implementation handles
        """
        pass
