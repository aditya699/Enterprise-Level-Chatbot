import os
from typing import Dict
import requests

# Get and print credentials for debugging
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

print("Loaded credentials:")
print(f"Client ID: {CLIENT_ID}")
print(f"Client Secret exists: {'Yes' if CLIENT_SECRET else 'No'}")  # Don't print actual secret
print(f"Redirect URI: {REDIRECT_URI}")

def get_google_auth_url() -> str:
    """Generate URL for Google login"""
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "email profile openid",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"{base_url}?"
    auth_url += "&".join(f"{key}={value}" for key, value in params.items())
    return auth_url

def get_google_user_info(code: str) -> Dict:
    """Get user info from Google using auth code"""
    if not CLIENT_SECRET:
        raise ValueError("GOOGLE_CLIENT_SECRET is not set in environment variables")
        
    # Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    token_response = requests.post(token_url, data=token_data)
    
    if token_response.status_code != 200:
        print(f"Token error response: {token_response.text}")
        raise Exception(f"Failed to get token: {token_response.text}")
        
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    
    if not access_token:
        raise Exception("No access token in response")
    
    # Get user info
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)
    return user_response.json()