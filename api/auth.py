from fastapi import APIRouter, HTTPException

from api.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from db.mysql_store import (
    create_user,
    get_user_by_email,
    get_user_by_verification_token,
    verify_user_email,
    get_user_by_reset_token,
    set_reset_token,
    reset_user_password
)

from services.password import (
    hash_password,
    verify_password
)

from services.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token
)

from services.email import (
    send_verification_email,
    send_password_reset_email
)

import re
import secrets

from datetime import datetime, timedelta


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================================================
# VALIDATION
# =========================================================

def validate_name(name: str):

    name = name.strip()

    if len(name) < 2:
        raise HTTPException(
            status_code=400,
            detail="Name must contain at least 2 characters"
        )

    if len(name) > 100:
        raise HTTPException(
            status_code=400,
            detail="Name is too long"
        )

    if not re.fullmatch(
        r"[A-Za-z]+(?:[ '-][A-Za-z]+)*",
        name
    ):
        raise HTTPException(
            status_code=400,
            detail="Name contains invalid characters"
        )

    return name


def validate_email(email: str):

    email = email.strip().lower()

    pattern = (
    r"^[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)
    if not re.fullmatch(pattern, email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email address"
        )

    return email


# =========================================================
# REGISTER
# =========================================================

@router.post("/register")
def register_user(request: RegisterRequest):

    # Validate name
    name = validate_name(request.name)

    # Validate email
    email = validate_email(request.email)

    # Check existing user
    existing_user = get_user_by_email(email)

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(
        request.password
    )

    # Generate verification token
    verification_token = secrets.token_urlsafe(32)

    # Verification valid for 30 minutes
    verification_expires = (
        datetime.now()
        + timedelta(minutes=30)
    )

    # Create user
    user_id = create_user(
        name,
        email,
        password_hash,
        verification_token,
        verification_expires
    )

    # Send verification email
    email_sent = send_verification_email(
        email,
        verification_token
    )

    if not email_sent:

        raise HTTPException(
            status_code=500,
            detail=(
                "Account created but verification "
                "email could not be sent."
            )
        )

    return {

        "success": True,

        "message": (
            "Registration successful. "
            "Please check your email to verify your account."
        ),

        "user_id": user_id,

        "email": email
    }


# =========================================================
# VERIFY EMAIL
# =========================================================

@router.get("/verify-email")
def verify_email(token: str):

    # Find user
    user = get_user_by_verification_token(
        token
    )

    if user is None:

        raise HTTPException(
            status_code=400,
            detail="Invalid verification token"
        )

    # Already verified
    if user["is_verified"]:

        return {

            "success": True,

            "message": "Email is already verified."
        }

    # Check expiry
    if (
        user["verification_expires"] is None
        or
        datetime.now()
        > user["verification_expires"]
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Verification link has expired. "
                "Please register again."
            )
        )

    # Verify email
    verify_user_email(
        user["id"]
    )

    return {

        "success": True,

        "message": (
            "Email verified successfully. "
            "You can now login."
        )
    }


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login_user(request: LoginRequest):

    # Validate email
    email = validate_email(
        request.email
    )

    # Find user
    user = get_user_by_email(email)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check email verification
    if not user["is_verified"]:

        raise HTTPException(
            status_code=403,
            detail=(
                "Please verify your email "
                "before logging in."
            )
        )

    # Verify password
    password_valid = verify_password(
        request.password,
        user["password_hash"]
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create access token
    access_token = create_access_token(
        user["id"],
        user["email"]
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        user["id"],
        user["email"]
    )

    return {

        "success": True,

        "message": "Login successful",

        "user_id": user["id"],

        "name": user["name"],

        "email": user["email"],

        "access_token": access_token,

        "refresh_token": refresh_token
    }


# =========================================================
# REFRESH ACCESS TOKEN
# =========================================================

@router.post("/refresh")
def refresh_access_token(
    request: RefreshTokenRequest
):

    payload = verify_token(
        request.refresh_token
    )

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    # Make sure this is a refresh token
    if payload.get("token_type") != "refresh":

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    # Get user
    user = get_user_by_email(
        payload["email"]
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # Check verification
    if not user["is_verified"]:

        raise HTTPException(
            status_code=403,
            detail="Email is not verified"
        )

    # Create new access token
    new_access_token = create_access_token(
        user["id"],
        user["email"]
    )

    return {

        "success": True,

        "message": (
            "Access token refreshed successfully"
        ),

        "user_id": user["id"],

        "name": user["name"],

        "email": user["email"],

        "access_token": new_access_token
    }


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest
):

    # Validate email
    email = validate_email(
        request.email
    )

    # Find user
    user = get_user_by_email(email)

    # Don't reveal whether account exists
    if user is None:

        return {

            "success": True,

            "message": (
                "If an account exists with this email, "
                "a password reset link has been sent."
            )
        }

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)

    # Reset link valid for 30 minutes
    reset_token_expires = (
        datetime.now()
        + timedelta(minutes=30)
    )

    # Save reset token
    set_reset_token(
        user["id"],
        reset_token,
        reset_token_expires
    )

    # Send email
    email_sent = send_password_reset_email(
        email,
        reset_token
    )

    if not email_sent:

        raise HTTPException(
            status_code=500,
            detail="Unable to send password reset email"
        )

    return {

        "success": True,

        "message": (
            "If an account exists with this email, "
            "a password reset link has been sent."
        )
    }


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest
):

    # Find user using reset token
    user = get_user_by_reset_token(
        request.token
    )

    if user is None:

        raise HTTPException(
            status_code=400,
            detail="Invalid password reset token"
        )

    # Check expiry
    if (
        user["reset_token_expires"] is None
        or
        datetime.now()
        > user["reset_token_expires"]
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Password reset link has expired."
            )
        )

    # Hash new password
    password_hash = hash_password(
        request.new_password
    )

    # Update password and remove reset token
    reset_user_password(
        user["id"],
        password_hash
    )

    return {

        "success": True,

        "message": (
            "Password reset successfully. "
            "You can now login with your new password."
        )
    }