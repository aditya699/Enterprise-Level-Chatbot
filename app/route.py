# app/route.py
from fastapi import APIRouter, HTTPException, Depends
from app.models import UserMessage
from app.services import get_chat_response
from fastapi.responses import JSONResponse
from app.auth.sessions import verify_session
from app.database import get_db_connection

api_router = APIRouter()

@api_router.post("/chat")
async def chat_response(
    user_message: UserMessage,
    user: dict = Depends(verify_session)
):
    try:
        # Store user message in database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert user's message
            cursor.execute("""
                INSERT INTO Messages (user_id, content, is_user_message)
                VALUES (?, ?, 1)
            """, (user["user_id"], user_message.user_message))
            
            # Get response from Claude
            response = get_chat_response(user_message)
            
            # Store Claude's response
            cursor.execute("""
                INSERT INTO Messages (user_id, content, is_user_message)
                VALUES (?, ?, 0)
            """, (user["user_id"], response))
            
            conn.commit()
            
            return JSONResponse(content={"response": response})
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/messages")
async def get_messages(
    user: dict = Depends(verify_session)
):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get all messages for the user
            cursor.execute("""
                SELECT content, is_user_message, created_at
                FROM Messages
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 50  -- Limit to last 50 messages
            """, (user["user_id"],))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "content": row[0],
                    "is_user_message": bool(row[1]),
                    "created_at": row[2].isoformat()
                })
            
            return JSONResponse(content={"messages": messages})
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))