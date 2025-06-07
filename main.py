import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base, engine

# Configure logging
logging.basicConfig(
    level=get_settings().LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("invoice-agent")

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Invoice Agent Authentication Service",
    description="API service for handling authentication with accounting systems",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=get_settings().API_V1_PREFIX)

# Log application startup information
settings = get_settings()
logger.info(f"Starting application in {settings.APP_ENV} environment")
logger.info(f"API endpoints available at: {settings.API_V1_PREFIX}")

# Log authentication status
if settings.APP_ENV == "development":
    auth_status = "DISABLED" if not settings.AUTH_ENABLED else "ENABLED"
    logger.warning(f"Authentication is {auth_status} in development mode")
    
    if not settings.AUTH_ENABLED:
        logger.info("Development endpoints available at /api/v1/dev")
        logger.info("Mock users will be provided for authenticated endpoints")
else:
    # Always log when authentication is disabled in non-development environments
    if not settings.AUTH_ENABLED:
        logger.warning("WARNING: Authentication is DISABLED in non-development environment!")
    else:
        logger.info("Authentication is enabled")


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
