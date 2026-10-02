from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    session_id: int

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    
class LoginRequest(BaseModel):
    email: str
    password: str  

class RefreshTokenRequest(BaseModel):
    refresh_token: str