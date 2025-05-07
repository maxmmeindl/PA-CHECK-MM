"""
Main FastAPI application for the PA-CHECK-MM API.

This module defines the main FastAPI application and includes the API routers.
"""
import logging
from typing import Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from .models import ErrorResponse
from .routers import router as workflow_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")


# Create FastAPI application
app = FastAPI(
    title="PA-CHECK-MM API",
    description="API for the PA-CHECK-MM Enterprise Solution",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(workflow_router)


# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the API."""
    logger.exception(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type=exc.__class__.__name__
        ).dict(),
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """Root endpoint for the API."""
    return {
        "message": "Welcome to the PA-CHECK-MM API",
        "docs": "/docs",
        "version": app.version,
    }


# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> JSONResponse:
    """Custom Swagger UI endpoint."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
        swagger_favicon_url="",
    )


# Custom OpenAPI endpoint
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint() -> Dict:
    """Custom OpenAPI endpoint."""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for the API."""
    return {"status": "healthy"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
