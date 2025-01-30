"""
CORS middleware configuration for the API service.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI) -> None:
    """Setup CORS middleware"""
    origins = [
        "http://localhost:5173",  # Frontend dev server
        "http://localhost:8001",  # Explorer backend
        "http://localhost:3000",  # Alternative frontend port
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 