import os
import smtplib

from email.message import EmailMessage

from utils.logger import get_logger


logger = get_logger(__name__)


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_EMAIL = os.getenv(
    "SMTP_EMAIL"
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD"
)


# =========================================================
# Verification Email
# =========================================================

def send_verification_email(
    recipient_email,
    verification_token
):

    try:

        verification_url = (
            "http://localhost:8000/auth/verify-email"
            f"?token={verification_token}"
        )

        message = EmailMessage()

        message["Subject"] = (
            "Verify your email - PDF RAG Chatbot"
        )

        message["From"] = SMTP_EMAIL

        message["To"] = recipient_email

        message.set_content(
            f"""
Hello,

Thank you for registering with PDF RAG Chatbot.

Please verify your email address by clicking the link below:

{verification_url}

This verification link will expire in 30 minutes.

If you did not create this account, you can safely ignore this email.

Regards,
PDF RAG Chatbot
"""
        )

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                SMTP_EMAIL,
                SMTP_PASSWORD
            )

            server.send_message(
                message
            )

        logger.info(
            f"Verification email sent to {recipient_email}"
        )

        return True

    except Exception as e:

        logger.error(
            f"Error sending verification email: {e}"
        )

        return False


# =========================================================
# Password Reset Email
# =========================================================

def send_password_reset_email(
    recipient_email,
    reset_token
):

    try:

        # =========================================
        # IMPORTANT:
        # Reset link opens Streamlit frontend
        # instead of directly calling FastAPI.
        # =========================================

        reset_url = (
            "http://localhost:8501"
            f"?reset_token={reset_token}"
        )

        message = EmailMessage()

        message["Subject"] = (
            "Reset your password - PDF RAG Chatbot"
        )

        message["From"] = SMTP_EMAIL

        message["To"] = recipient_email

        message.set_content(
            f"""
Hello,

We received a request to reset your password
for PDF RAG Chatbot.

Please click the link below to reset your password:

{reset_url}

This password reset link will expire in 30 minutes.

If you did not request a password reset,
you can safely ignore this email.

Regards,
PDF RAG Chatbot
"""
        )

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                SMTP_EMAIL,
                SMTP_PASSWORD
            )

            server.send_message(
                message
            )

        logger.info(
            f"Password reset email sent to {recipient_email}"
        )

        return True

    except Exception as e:

        logger.error(
            f"Error sending password reset email: {e}"
        )

        return False