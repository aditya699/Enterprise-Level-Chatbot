from dotenv import load_dotenv
import os

# Load .env file at the very start
load_dotenv()

# Debug print all env variables we need
print("\nChecking environment variables:")
print(f"GOOGLE_CLIENT_ID exists: {'Yes' if os.getenv('GOOGLE_CLIENT_ID') else 'No'}")
print(f"GOOGLE_CLIENT_SECRET exists: {'Yes' if os.getenv('GOOGLE_CLIENT_SECRET') else 'No'}")
print(f"GOOGLE_REDIRECT_URI exists: {'Yes' if os.getenv('GOOGLE_REDIRECT_URI') else 'No'}\n")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.route import api_router
from app.auth.router import router as auth_router

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
    # Serve login page first
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat")
async def chat(request: Request):
    # This will be our protected chat route
    # TODO: Add authentication check here
    return templates.TemplateResponse("index.html", {"request": request})