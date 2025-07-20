from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.routers import auth, content, scheduler, analytics, social_accounts # Assuming these are the unified routers
from app.core.celery_app import celery_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Create all tables if they don't exist
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Social Media Automation Platform",
    description="Complete social media automation and management platform",
    version="1.0.0",
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS, # This needs to be defined in settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(social_accounts.router, prefix="/api/accounts", tags=["Social Accounts"])
app.include_router(content.router, prefix="/api/content", tags=["Content Management"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["Scheduling"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Social Media Automation Platform API!"}

# Example of a missing settings.BACKEND_CORS_ORIGINS
# This would typically be defined in app/core/config.py
# For now, adding a placeholder for demonstration
if not hasattr(settings, 'BACKEND_CORS_ORIGINS'):
    settings.BACKEND_CORS_ORIGINS = ["http://localhost:3000", "https://yourdomain.com"]
