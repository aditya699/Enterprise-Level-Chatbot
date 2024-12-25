from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from . import utils
from .sessions import create_session_token  # Add this import
from ..database import get_db_connection  # Add this import
from datetime import datetime, timedelta, timezone
router = APIRouter()

@router.get("/login")
async def login():
    """Redirect to Google login"""
    auth_url = utils.get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(code: str):
    try:
        # Get user info from Google
        try:
            user_info = utils.get_google_user_info(code)
        except Exception as e:
            print("Debug - Google auth error:", str(e))
            return RedirectResponse(url="/login?error=Failed to get user info")

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("""
                    SELECT id FROM Users 
                    WHERE email = ?
                """, (user_info['email'],))
                
                user_row = cursor.fetchone()
                user_id = user_row[0] if user_row else None
                
                if not user_id:
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

                session_token = create_session_token(user_info['email'])
                print("Debug - Created new session token:", session_token)

                # Store in database
                cursor.execute("""
                    INSERT INTO Sessions (user_id, session_token, expires_at)
                    VALUES (?, ?, DATEADD(day, 1, GETDATE()))
                """, (user_id, session_token))
                
                conn.commit()
                print("Debug - Stored session in database")

                response = RedirectResponse(url="/chat")
                
                # Set cookie with minimal secure settings for localhost
                response.set_cookie(
                    key="session_token",
                    value=session_token,
                    secure=False,  # Allow HTTP for localhost
                    httponly=True,
                    samesite="Lax",
                    max_age=86400,  # 24 hours in seconds
                    path="/",    
                    expires=datetime.now(timezone.utc) + timedelta(days=1),
                    domain=None  # Let browser determine domain
                )
                print("Debug - Set cookie in response")
                
                return response

        except Exception as db_error:
            print("Debug - Database error:", str(db_error))
            return RedirectResponse(url="/login?error=Database error")

    except Exception as e:
        print("Debug - Unexpected error:", str(e))
        return RedirectResponse(url="/login?error=Unknown error")