from fastapi import APIRouter

from app.api.routes import auth
from app.core.config import get_settings

# Create main API router
api_router = APIRouter()
settings = get_settings()

# Include routes from different modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Add development endpoints only in development mode
if settings.APP_ENV == "development":
    from app.api.routes import dev
    api_router.include_router(dev.router, prefix="/dev", tags=["Development"])

# Add more routers here as the application grows
# api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
