from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    role: str = "user"  # Puede ser "admin" o "user"
    daily_tokens: int = 40

class UserCreate(UserBase):
    password: str

class GenerateRequest(BaseModel):
    prompt: str
    file_type: str  # Formatos: "pdf", "word", "excel", "algorithm"