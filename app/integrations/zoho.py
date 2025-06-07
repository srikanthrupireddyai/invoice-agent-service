import httpx
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from app.core.config import get_settings
from app.integrations.base import AccountingIntegrationBase
from app.db.models import IntegrationType

settings = get_settings()
logger = logging.getLogger(__name__)


class ZohoIntegration(AccountingIntegrationBase):
    """
    Implementation of Zoho Books/Invoice API integration
    """
    def __init__(self):
        self.client_id = settings.ZOHO_CLIENT_ID
        self.client_secret = settings.ZOHO_CLIENT_SECRET
        self.redirect_uri = settings.ZOHO_REDIRECT_URI
        self.token_url = settings.ZOHO_TOKEN_URL
    
    def get_integration_type(self) -> str:
        """Return the integration type"""
        return IntegrationType.ZOHO
    
    async def exchange_auth_code(self, auth_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        """
        request_data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": auth_code
        }
        
        # Log the request data (mask sensitive information)
        safe_log_data = request_data.copy()
        safe_log_data["client_secret"] = "***MASKED***" 
        safe_log_data["code"] = "***MASKED***"
        logger.info(json.dumps({"ZOHO API REQUEST [exchange_auth_code]": safe_log_data}, indent=2))
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=request_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Log the response
            response_data = response.json() if response.content else {}
            status_code = response.status_code
            
            # Create a safe copy for logging, masking sensitive info
            safe_response = response_data.copy() if response_data else {}
            if "access_token" in safe_response:
                safe_response["access_token"] = "***MASKED***"
            if "refresh_token" in safe_response:
                safe_response["refresh_token"] = "***MASKED***"
                
            logger.info(json.dumps({"ZOHO API RESPONSE [exchange_auth_code]": {"status_code": status_code, "response": safe_response}}, indent=2))
            
            if status_code != 200:
                error_message = f"Failed to retrieve access token: {status_code}"
                logger.error(json.dumps({"error": error_message, "response": safe_response}, indent=2))
                raise ValueError(f"{error_message}, {safe_response}")
            
            return response_data
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Use refresh token to get a new access token when current one expires
        """
        request_data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        
        # Log the request data (mask sensitive information)
        safe_log_data = request_data.copy()
        safe_log_data["client_secret"] = "***MASKED***" 
        safe_log_data["refresh_token"] = "***MASKED***"
        logger.info(json.dumps({"ZOHO API REQUEST [refresh_access_token]": safe_log_data}, indent=2))
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=request_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Log the response
            response_data = response.json() if response.content else {}
            status_code = response.status_code
            
            # Create a safe copy for logging, masking sensitive info
            safe_response = response_data.copy() if response_data else {}
            if "access_token" in safe_response:
                safe_response["access_token"] = "***MASKED***"
            if "refresh_token" in safe_response:
                safe_response["refresh_token"] = "***MASKED***"
                
            logger.info(json.dumps({"ZOHO API RESPONSE [refresh_access_token]": {"status_code": status_code, "response": safe_response}}, indent=2))
            
            if status_code != 200:
                error_message = f"Failed to refresh access token: {status_code}"
                logger.error(json.dumps({"error": error_message, "response": safe_response}, indent=2))
                raise ValueError(f"{error_message}, {safe_response}")
            
            return response_data
    
    async def get_token_expiry(self, token_data: Dict[str, Any]) -> datetime:
        """
        Calculate token expiry datetime from token data
        """
        # Zoho API returns expires_in in seconds
        expires_in = int(token_data.get("expires_in", 3600))
        return datetime.utcnow() + timedelta(seconds=expires_in)
