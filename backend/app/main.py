"""
    FastAPI entrypoint for the Photo Contour backend.

    Creates the FastAPI application instance, configures middleware,
    includes all API routers, and exposes the ASGI app object
    used by the server (uvicorn/gunicorn).
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings


# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS middleware (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (uploads folder)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint - basic health check."""
    return {"message": "Photo Contour API is running", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns 200 OK if the API is running and database is accessible.
    """
    return {
        "status": "healthy",
        "database": settings.DATABASE_URL.split("://")[0],
        "upload_dir": settings.UPLOAD_DIR
    }
    

@app.get("/ping")
async def ping():
    """Simple ping endpoint for load balancer health checks."""
    return {"pong": True}