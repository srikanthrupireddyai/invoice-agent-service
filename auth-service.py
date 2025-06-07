from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Environment variables
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
ZOHO_TOKEN_URL = "https://accounts.zoho.in/oauth/v2/token"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # Generate via Fernet.generate_key()

# Setup Fernet for encryption
encryptor = Fernet(ENCRYPTION_KEY)

app = FastAPI()

# Pydantic schema for request body
class AuthCodeRequest(BaseModel):
    auth_code: str
    user_id: int  # Or other identifier to associate with the integration

# Simulated DB table as dictionary (in-memory)
integration_keys_db = {}

@app.post("/zoho/auth")
async def zoho_auth_handler(payload: AuthCodeRequest):
    try:
        # Step 1: Exchange auth_code for access_token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ZOHO_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": ZOHO_CLIENT_ID,
                    "client_secret": ZOHO_CLIENT_SECRET,
                    "redirect_uri": ZOHO_REDIRECT_URI,
                    "code": payload.auth_code
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to retrieve access token")

        token_data = response.json()

        # Step 2: Encrypt tokens before saving
        encrypted_access_token = encryptor.encrypt(token_data["access_token"].encode()).decode()
        encrypted_refresh_token = encryptor.encrypt(token_data["refresh_token"].encode()).decode()

        # Step 3: Save to integration_keys_db (simulate DB insert)
        integration_keys_db[payload.user_id] = {
            "access_token": encrypted_access_token,
            "refresh_token": encrypted_refresh_token,
            "expires_in": token_data["expires_in"]
        }

        return {"status": "success", "message": "Tokens stored successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Future modularization: extract to modules like
# - auth_service.py (for zoho token exchange logic)
# - encrypt_utils.py (for encryption logic)
# - database.py (for DB interactions)
# - schemas.py (for Pydantic models)
# - routers/zoho.py (for API routes)

# Example encryption key generation (run once and store securely)
# from cryptography.fernet import Fernet
# print(Fernet.generate_key())