import streamlit as st

from frontend.login_page import (
    show_login_page,
    show_register_page
)

from frontend.document_manager import (
    show_document_manager
)

from frontend.chat_interface import (
    show_chat_interface
)


# =========================================
# Page Configuration
# =========================================

st.set_page_config(
    page_title="RAG PDF Chatbot",
    layout="wide"
)


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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_register" not in st.session_state:
    st.session_state.show_register = False


# =========================================
# Authentication Check
# =========================================

if not st.session_state.access_token:

    # -----------------------------------------
    # Register Page
    # -----------------------------------------

    if st.session_state.show_register:

        show_register_page()

        st.markdown("---")

        if st.button(
            "Already have an account? Login"
        ):

            st.session_state.show_register = False

            st.rerun()

    # -----------------------------------------
    # Login Page
    # -----------------------------------------

    else:

        show_login_page()

        st.markdown("---")

        if st.button(
            "Don't have an account? Register"
        ):

            st.session_state.show_register = True

            st.rerun()


# =========================================
# Main Application
# =========================================

else:

    # -----------------------------------------
    # Header
    # -----------------------------------------

    st.title("RAG PDF Chatbot")

    st.sidebar.success(
        f"Welcome, {st.session_state.user_name}"
    )

    st.sidebar.caption(
        st.session_state.user_email
    )

    # -----------------------------------------
    # Logout
    # -----------------------------------------

    if st.sidebar.button(
        "Logout"
    ):

        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.session_state.chat_history = []

        st.rerun()

    # -----------------------------------------
    # Document Manager
    # -----------------------------------------

    show_document_manager()

    # -----------------------------------------
    # Chat Interface
    # -----------------------------------------

    show_chat_interface()