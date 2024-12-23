from langchain_anthropic import ChatAnthropic
from fastapi import HTTPException
import os
from app.models import UserMessage
from dotenv import load_dotenv

load_dotenv()

os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')

llm = ChatAnthropic(
    model='claude-3-haiku-20240307',
    temperature=0,
    max_tokens=1024,
    timeout=20,  # Added timeout
    max_retries=2,
)

def get_chat_response(user_message: UserMessage) -> str:
    try:
        response = llm.invoke(user_message.user_message)
        return str(response.content)  # Ensure we're returning a string
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))