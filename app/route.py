# app/route.py
from fastapi import APIRouter, HTTPException, Depends
from app.models import UserMessage
from app.services import get_chat_response
from fastapi.responses import JSONResponse
from app.auth.sessions import verify_session

api_router = APIRouter()

@api_router.post("/chat")
async def chat_response(
    user_message: UserMessage,
    user: dict = Depends(verify_session)  # This protects our route
):
    try:
        # Now we can use the user info if needed
        response = get_chat_response(user_message)
        return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))