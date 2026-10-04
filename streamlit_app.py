import os
import streamlit as st

from streamlit_cookies_manager import EncryptedCookieManager

from frontend.login_page import (
    show_login_page,
    show_register_page,
    show_forgot_password_page,
    show_reset_password_page
)

from frontend.document_manager import (
    show_document_manager,
    show_pdf_viewer
)

from frontend.chat_interface import (
    show_chat_interface
)

from frontend.api_client import (
    refresh_access_token
)


# =========================================
# Page Configuration
# =========================================

st.set_page_config(
    page_title="RAG PDF Chatbot",
    layout="wide"
)


# =========================================
# Cookie Manager
# =========================================

cookies = EncryptedCookieManager(

    prefix="rag_pdf_chatbot/",

    password=os.getenv(
        "COOKIES_PASSWORD",
        "rag-pdf-chatbot-development-secret"
    )
)

if not cookies.ready():
    st.stop()


# =========================================
# Session State Initialization
# =========================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# =========================================
# Chat State
# =========================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "active_document_id" not in st.session_state:
    st.session_state.active_document_id = None

if "active_document_filename" not in st.session_state:
    st.session_state.active_document_filename = None

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "history_loaded_for" not in st.session_state:
    st.session_state.history_loaded_for = None

if "show_register" not in st.session_state:
    st.session_state.show_register = False


# =========================================
# New Authentication State
# =========================================

if "registration_success" not in st.session_state:
    st.session_state.registration_success = False

if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False

if "show_reset_password" not in st.session_state:
    st.session_state.show_reset_password = False

if "reset_token" not in st.session_state:
    st.session_state.reset_token = None


# =========================================
# Read Reset Token From URL
# =========================================

query_params = st.query_params

reset_token = st.query_params.get(
    "reset_token"
)
if reset_token:

    st.session_state.reset_token = reset_token

    st.session_state.show_reset_password = True

    st.session_state.show_forgot_password = False

    st.session_state.show_register = False


# =========================================
# Restore Login After Browser Refresh
# =========================================

if not st.session_state.access_token:

    saved_refresh_token = cookies.get(
        "refresh_token"
    )

    if saved_refresh_token:

        try:

            data = refresh_access_token(
                saved_refresh_token
            )

            if data.get("success"):

                st.session_state.access_token = (
                    data["access_token"]
                )

                st.session_state.refresh_token = (
                    saved_refresh_token
                )

                st.session_state.user_id = (
                    data["user_id"]
                )

                st.session_state.user_name = (
                    data["name"]
                )

                st.session_state.user_email = (
                    data["email"]
                )

        except Exception:

            cookies["refresh_token"] = ""
            cookies.save()

            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.user_email = None


# =========================================
# Authentication Check
# =========================================

if not st.session_state.access_token:

    # =====================================
    # Reset Password
    # =====================================

    if (
        st.session_state.show_reset_password
        and st.session_state.reset_token
    ):

        show_reset_password_page(
            st.session_state.reset_token
        )


    # =====================================
    # Forgot Password
    # =====================================

    elif st.session_state.show_forgot_password:

        show_forgot_password_page()


    # =====================================
    # Register
    # =====================================

    elif st.session_state.show_register:

        show_register_page()

        st.markdown("---")

        if st.button(
            "Already have an account? Login"
        ):

            st.session_state.show_register = False

            st.session_state.registration_success = False

            st.rerun()


    # =====================================
    # Login
    # =====================================

    else:

        show_login_page(cookies)

        st.markdown("---")

        if st.button(
            "Don't have an account? Register"
        ):

            st.session_state.show_register = True

            st.session_state.show_forgot_password = False

            st.session_state.registration_success = False

            st.rerun()


# =========================================
# Main Application
# =========================================

else:

    st.title(
        "RAG PDF Chatbot"
    )

    st.sidebar.success(
        f"Welcome, {st.session_state.user_name}"
    )

    st.sidebar.caption(
        st.session_state.user_email
    )


    # =====================================
    # Logout
    # =====================================

    if st.sidebar.button(
        "Logout"
    ):

        # Delete browser cookie
        cookies["refresh_token"] = ""
        cookies.save()

        # Authentication
        st.session_state.access_token = None
        st.session_state.refresh_token = None

        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_email = None

        # Chat
        st.session_state.chat_history = []

        st.session_state.active_document_id = None
        st.session_state.active_document_filename = None
        st.session_state.active_session_id = None
        st.session_state.history_loaded_for = None

        # Authentication UI
        st.session_state.show_register = False
        st.session_state.registration_success = False
        st.session_state.show_forgot_password = False
        st.session_state.show_reset_password = False
        st.session_state.reset_token = None

        # PDF viewer
        st.session_state.pop(
            "viewed_pdf",
            None
        )

        st.session_state.pop(
            "viewed_filename",
            None
        )

        st.rerun()


    # =====================================
    # Document Manager
    # =====================================

    show_document_manager()


    # =====================================
    # PDF Viewer
    # =====================================

    show_pdf_viewer()


    # =====================================
    # Chat Interface
    # =====================================

    show_chat_interface()