# app/auth/session.py
from fastapi import Request, HTTPException
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from ..database import get_db_connection
from fastapi.responses import RedirectResponse

SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SESSION_SECRET_KEY must be set in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
def create_session_token(email: str) -> str:
    """Create a new session token for a user"""
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    data = {
        "sub": email,  # subject (user identifier)
        "exp": expires,  # expiration time
        "iat": datetime.now(timezone.utc)  # issued at
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
# app/auth/session.py
async def verify_session(request: Request):
    """
    Verify session token from cookie and database.
    If invalid, redirect to login.
    """
    print("Verifying session...")
    
    # 1. Check if cookie exists
    session_token = request.cookies.get("session_token")
    if not session_token:
        print("No session token - redirecting to login")
        return RedirectResponse(url="/auth/login")
    
    # 2. Verify JWT token
    email = verify_session_token(session_token)
    if not email:
        print("Invalid token - redirecting to login")
        return RedirectResponse(url="/auth/login")
    
    # 3. Check if session exists in database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.email
            FROM Sessions s
            JOIN Users u ON s.user_id = u.id
            WHERE s.session_token = ? 
            AND s.expires_at > GETDATE()
        """, (session_token,))
        
        session = cursor.fetchone()
        if not session:
            print("Session not found - redirecting to login")
            return RedirectResponse(url="/auth/login")
        
        # Return user info for the route to use
        return {"user_id": session[0], "email": session[1]}