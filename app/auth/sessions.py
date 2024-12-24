# app/auth/session.py
from fastapi import Request, HTTPException
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta, UTC
from typing import Optional

SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SESSION_SECRET_KEY must be set in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_session_token(email: str) -> str:
    """Create a new session token for a user"""
    expires = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    data = {
        "sub": email,  # subject (user identifier)
        "exp": expires,  # expiration time
        "iat": datetime.now(UTC)  # issued at
    }
    
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_session_token(token: str) -> Optional[str]:
    """
    Verify a session token and return the user's email if valid
    Returns None if token is invalid
    """
    try:
        # This will verify signature and expiration automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None