from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from . import utils
from .sessions import create_session_token  # Add this import
from ..database import get_db_connection  # Add this import

router = APIRouter()

@router.get("/login")
async def login():
    """Redirect to Google login"""
    auth_url = utils.get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(code: str):
    user_info = utils.get_google_user_info(code)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("""
            SELECT id FROM Users 
            WHERE email = ?
        """, (user_info['email'],))
        
        user_row = cursor.fetchone()
        
        if user_row:
            # Existing user - update last login
            cursor.execute("""
                UPDATE Users 
                SET last_login = GETDATE()
                WHERE email = ?
            """, (user_info['email'],))
            user_id = user_row[0]
        else:
            # New user - insert
            cursor.execute("""
                INSERT INTO Users (email, name, picture_url, google_id)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?)
            """, (
                user_info['email'],
                user_info['name'],
                user_info['picture'],
                user_info['id']
            ))
            user_id = cursor.fetchone()[0]

        # Create session token
        session_token = create_session_token(user_info['email'])

        # Store in database
        cursor.execute("""
            INSERT INTO Sessions (user_id, session_token, expires_at)
            VALUES (?, ?, DATEADD(day, 1, GETDATE()))
        """, (user_id, session_token))
        
        conn.commit()

        # Create response with redirect
        response = RedirectResponse(url="/chat")
        
        # Set the session token as cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,   # Prevents JavaScript access
            secure=True,     # Only sent over HTTPS
            samesite="lax",  # CSRF protection
            max_age=60 * 60 * 24  # 24 hours
        )
        
        return response