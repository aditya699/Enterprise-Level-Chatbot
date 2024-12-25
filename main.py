import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.route import api_router
from app.auth.router import router as auth_router
from app.auth.sessions import verify_session
from app.database import get_db_connection  # Added this import


# Load .env file at the very start
load_dotenv()

# Debug print all env variables we need
print("\nChecking environment variables:")
print(f"GOOGLE_CLIENT_ID exists: {'Yes' if os.getenv('GOOGLE_CLIENT_ID') else 'No'}")
print(f"GOOGLE_CLIENT_SECRET exists: {'Yes' if os.getenv('GOOGLE_CLIENT_SECRET') else 'No'}")
print(f"GOOGLE_REDIRECT_URI exists: {'Yes' if os.getenv('GOOGLE_REDIRECT_URI') else 'No'}\n")

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
    try:
        # Debug all cookies
        print("Debug - All cookies:", request.cookies)
        
        session_token = request.cookies.get("session_token")
        print("Debug - Session token from cookie:", session_token)
        
        if session_token:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # Check both Sessions and Users tables
                    query = """
                        SELECT 
                            u.id, 
                            u.email, 
                            s.expires_at,
                            s.session_token
                        FROM Sessions s
                        JOIN Users u ON s.user_id = u.id
                        WHERE s.session_token = ?
                    """
                    cursor.execute(query, (session_token,))
                    session = cursor.fetchone()
                    
                    if session:
                        print(f"Debug - Found session in DB: {session}")
                        # Check if session is expired
                        cursor.execute("SELECT GETDATE()")
                        current_time = cursor.fetchone()[0]
                        print(f"Debug - Current time: {current_time}")
                        print(f"Debug - Session expires: {session[2]}")
                        
                        if session[2] > current_time:
                            print("Debug - Session is valid, redirecting to chat")
                            return RedirectResponse(url="/chat")
                        else:
                            print("Debug - Session is expired")
                            response = templates.TemplateResponse(
                                "login.html", 
                                {"request": request, "error": "Session expired"}
                            )
                            response.delete_cookie(key="session_token", path="/")
                            return response
                    else:
                        print("Debug - No session found in database")
                        return templates.TemplateResponse("login.html", {"request": request})
            
            except Exception as db_error:
                print("Debug - Database error:", str(db_error))
                return templates.TemplateResponse(
                    "login.html", 
                    {"request": request, "error": str(db_error)}
                )
        else:
            print("Debug - No session token in cookie")
            return templates.TemplateResponse("login.html", {"request": request})
        
    except Exception as e:
        print("Debug - Unexpected error:", str(e))
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": str(e)}
        )

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