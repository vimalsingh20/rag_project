from fastapi import APIRouter, HTTPException

from api.schemas import RegisterRequest, LoginRequest

from db.mysql_store import (
    create_user,
    get_user_by_email
)

from services.password import hash_password ,verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register_user(request: RegisterRequest):

    existing_user = get_user_by_email(request.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    password_hash = hash_password(
        request.password
    )

    user_id = create_user(
        request.name,
        request.email,
        password_hash
    )

    return {
        "success": True,
        "message": "User registered successfully",
        "user_id": user_id
    }
    

@router.post("/login")
def login_user(request: LoginRequest):

    user = get_user_by_email(request.email)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_valid = verify_password(
        request.password,
        user["password_hash"]
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "success": True,
        "message": "Login successful",
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }