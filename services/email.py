import os
import smtplib

from email.message import EmailMessage

from utils.logger import get_logger


logger = get_logger(__name__)


# =========================================================
# SMTP CONFIGURATION
# =========================================================

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
# SEND VERIFICATION EMAIL
# =========================================================

def send_verification_email(
    recipient_email,
    verification_token
):

    try:

        # -----------------------------------------
        # Check SMTP configuration
        # -----------------------------------------

        if not SMTP_EMAIL:

            raise ValueError(
                "SMTP_EMAIL is not configured"
            )

        if not SMTP_PASSWORD:

            raise ValueError(
                "SMTP_PASSWORD is not configured"
            )

        # -----------------------------------------
        # Verification URL
        # -----------------------------------------

        verification_url = (
            "http://localhost:8000/auth/verify-email"
            f"?token={verification_token}"
        )

        # -----------------------------------------
        # Create email
        # -----------------------------------------

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

        # -----------------------------------------
        # Connect to Gmail SMTP
        # -----------------------------------------

        server = smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30
        )

        # -----------------------------------------
        # SMTP handshake
        # -----------------------------------------

        server.ehlo()

        # -----------------------------------------
        # Start TLS encryption
        # -----------------------------------------

        server.starttls()

        server.ehlo()

        # -----------------------------------------
        # Login
        # -----------------------------------------

        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        # -----------------------------------------
        # Send email
        # -----------------------------------------

        server.send_message(
            message
        )

        # -----------------------------------------
        # Close connection
        # -----------------------------------------

        server.quit()

        logger.info(
            f"Verification email sent to {recipient_email}"
        )

        return True

    except Exception as e:

        logger.error(
            f"Error sending verification email: {e}"
        )

        return False