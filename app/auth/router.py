from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from . import utils

router = APIRouter()

@router.get("/login")
async def login():
    """Redirect to Google login"""
    auth_url = utils.get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(code: str):
    """Handle Google OAuth callback"""
    user_info = utils.get_google_user_info(code)
    # For now, just return the user info
    return user_info