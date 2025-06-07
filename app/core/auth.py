"""
Authentication dependencies and utilities for FastAPI
"""
import json
import logging
import time
from typing import Dict, Optional, Union

import jwt
import requests
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.algorithms import RSAAlgorithm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import User, UserRole, UserStatus
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db

# Get application settings
settings = get_settings()

# Setup authentication scheme
security = HTTPBearer(auto_error=False)

# Configure logger
logger = logging.getLogger("app.auth")
logging_level = getattr(logging, settings.LOG_LEVEL)
logger.setLevel(logging_level)

# Cache for JWK keys - to avoid fetching on every request
jwk_keys: Dict = {}
last_jwk_fetch = 0
JWK_CACHE_DURATION = 3600  # 1 hour


def get_jwk_keys():
    """
    Fetch the JSON Web Keys from AWS Cognito for JWT validation
    Caches the keys to avoid frequent requests
    """
    global jwk_keys, last_jwk_fetch
    
    # Return cached keys if they're still valid
    if jwk_keys and time.time() - last_jwk_fetch < JWK_CACHE_DURATION:
        logger.debug("Using cached JWK keys")
        return jwk_keys
        
    # Fetch keys from Cognito
    jwk_url = f"https://cognito-idp.{settings.AWS_COGNITO_REGION}.amazonaws.com/{settings.AWS_COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    
    try:
        logger.info(f"Fetching JWK keys from: {jwk_url}")
        response = requests.get(jwk_url)
        response.raise_for_status()
        keys = response.json().get('keys', [])
        
        # Update the cache
        jwk_keys = {key['kid']: key for key in keys}
        last_jwk_fetch = time.time()
        logger.info(f"Successfully fetched {len(jwk_keys)} JWK keys")
        
        return jwk_keys
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching JWK keys: {str(e)}")
        return {}
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching JWK keys: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error fetching JWK keys: {str(e)}")
        return {}


def validate_token(token: str) -> Dict:
    """
    Validate a JWT token from AWS Cognito
    """
    if not token:
        logger.warning("Empty token provided for validation")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
        
    try:
        # Extract the header without validation to get the key ID
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        
        if not kid:
            logger.warning("Token missing kid in header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
            )
        
        # Fetch the JWK keys
        keys = get_jwk_keys()
        if not keys:
            logger.error("No JWK keys available for validation")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
            )
            
        if kid not in keys:
            logger.warning(f"Token kid {kid} not found in JWK keys")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
            )
            
        # Get the public key for validation
        public_key = RSAAlgorithm.from_jwk(json.dumps(keys[kid]))
        
        # Validate the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=settings.AWS_COGNITO_CLIENT_ID,
            options={"verify_exp": True}
        )
        
        logger.debug(f"Token validated successfully for subject: {payload.get('sub', 'unknown')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )


def create_mocked_user(db: Session) -> User:
    """
    Create a mocked user for development when AUTH_ENABLED is False
    """
    # Try to get an existing admin user
    user_repo = UserRepository(db)
    users = user_repo.get_all(limit=1)
    
    if users:
        # Return the first user if available
        return users[0]
    else:
        # If no users exist, this is likely a fresh database
        # Return a mocked user object without saving to DB
        # Note: This might cause issues if code explicitly depends on DB relationships
        # For a more robust solution, consider creating a test tenant and user
        return User(
            id=1,
            email="dev@example.com",
            first_name="Development",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            cognito_id="dev-user-id",
            tenant_id="00000000-0000-0000-0000-000000000000"
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user
    When AUTH_ENABLED is False, returns a development user
    """
    # If authentication is disabled, return mock user
    if not settings.AUTH_ENABLED:
        logger.info(f"Auth disabled: Using mock user for request to {request.url.path}")
        return create_mocked_user(db)
    
    # Check if credentials are provided
    if not credentials:
        logger.warning(f"Missing authentication header for request to {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Validate the token
    token = credentials.credentials
    payload = validate_token(token)
    
    # Extract Cognito user ID
    cognito_id = payload.get('sub')
    if not cognito_id:
        logger.warning("Token missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity in token",
        )
        
    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get_by_cognito_id(cognito_id)
    
    if not user:
        logger.warning(f"User with Cognito ID {cognito_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    # Check if user is active
    if user.status != UserStatus.ACTIVE:
        logger.warning(f"User {user.id} (Cognito ID: {cognito_id}) has inactive status: {user.status.value}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended",
        )
    
    logger.info(f"Authenticated user: {user.id} (email: {user.email}) for tenant: {user.tenant_id}")
    return user


async def check_admin_role(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to check if the current user has admin role
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user
