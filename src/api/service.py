"""
Main FastAPI application for the Vernachain API service.
"""

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from .middleware.cors import setup_cors
from .routes import auth, tokens, blockchain
from .database import init_db, get_db
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Vernachain API",
    description="API service for the Vernachain blockchain platform",
    version="0.1.0",
)

# Setup CORS
setup_cors(app)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tokens.router, prefix="/api/v1/tokens", tags=["Tokens"])
app.include_router(blockchain.router, prefix="/api/v1", tags=["Blockchain"])

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "up"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "down"

    return {
        "status": "healthy",
        "version": "0.1.0",
        "services": {
            "api": "up",
            "database": db_status
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal server error occurred"
            }
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Runs when the application starts"""
    logger.info("Starting Vernachain API service...")
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the application shuts down"""
    logger.info("Shutting down Vernachain API service...") 