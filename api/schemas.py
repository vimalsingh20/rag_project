from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str
    session_id: int


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str = Field(
        min_length=8,
        max_length=128
    )


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
    
class ForgotPasswordRequest(BaseModel):
    email: str
    
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        min_length=8,
        max_length=128
    )