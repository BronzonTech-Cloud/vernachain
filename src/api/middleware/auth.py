"""
Authentication middleware for the API service.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ..models import User

# Configuration
SECRET_KEY = "your-secret-key"  # TODO: Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: Dict[str, Any]) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from the JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # TODO: Get actual user from database
        return User(
            id="1",
            email=email,
            two_factor_enabled=False,
            created_at=datetime.utcnow()
        )
    except JWTError:
        raise credentials_exception

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # TODO: Implement actual password verification
    return True

def get_password_hash(password: str) -> str:
    """Get password hash"""
    # TODO: Implement actual password hashing
    return password 