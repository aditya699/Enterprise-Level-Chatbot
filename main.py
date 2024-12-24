from dotenv import load_dotenv
import os

# Load .env file at the very start
load_dotenv()

# Debug print all env variables we need
print("\nChecking environment variables:")
print(f"GOOGLE_CLIENT_ID exists: {'Yes' if os.getenv('GOOGLE_CLIENT_ID') else 'No'}")
print(f"GOOGLE_CLIENT_SECRET exists: {'Yes' if os.getenv('GOOGLE_CLIENT_SECRET') else 'No'}")
print(f"GOOGLE_REDIRECT_URI exists: {'Yes' if os.getenv('GOOGLE_REDIRECT_URI') else 'No'}\n")

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.route import api_router
from app.auth.router import router as auth_router
from app.auth.sessions import verify_session
from app.database import get_db_connection  # Added this import

app = FastAPI()
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="app/templates")

# Include routes
app.include_router(api_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root(request: Request):
    # Check for valid session first
    session_token = request.cookies.get("session_token")
    if session_token:
        # Verify the session
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
            if session:
                # Valid session exists, redirect to chat
                return RedirectResponse(url="/chat")
    
    # No valid session, show login page
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat")
async def chat(
    request: Request,
    user_info: dict = Depends(verify_session)
):
    # If we get here, user is authenticated (otherwise would have been redirected)
    if isinstance(user_info, RedirectResponse):
        return user_info  # Return the redirect if not authenticated
    
    print(f"Authenticated user accessing chat: {user_info.get('email')}")
    return templates.TemplateResponse("index.html", {"request": request})