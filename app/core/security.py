from cryptography.fernet import Fernet
from typing import Union

from app.core.config import get_settings

settings = get_settings()


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data
    """
    def __init__(self, key: str = settings.ENCRYPTION_KEY):
        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data and return as string
        """
        if isinstance(data, str):
            data = data.encode()
        
        encrypted_data = self.fernet.encrypt(data)
        return encrypted_data.decode()
    
    def decrypt(self, encrypted_data: Union[str, bytes]) -> str:
        """
        Decrypt data and return as string
        """
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
            
        decrypted_data = self.fernet.decrypt(encrypted_data)
        return decrypted_data.decode()


# Create a singleton instance for app-wide use
encryption_service = EncryptionService()
