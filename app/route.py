from fastapi import APIRouter, HTTPException
from app.models import UserMessage
from app.services import get_chat_response
from fastapi.responses import JSONResponse

api_router = APIRouter()

@api_router.post("/chat")
async def chat_response(user_message: UserMessage):
    try:
        response = get_chat_response(user_message)
        return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))