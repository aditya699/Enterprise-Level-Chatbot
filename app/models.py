from pydantic import BaseModel,Field
from typing import Literal


class UserMessage(BaseModel):
    user_message:str