from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    
class LoginRequest(BaseModel):
    email: str
    password: str    