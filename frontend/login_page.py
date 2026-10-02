import streamlit as st

from streamlit_cookies_controller import CookieController

from frontend.api_client import (
    login_user,
    register_user
)


# =========================================
# Cookie Controller
# =========================================

cookie_controller = CookieController()


# =========================================
# Login Page
# =========================================

def show_login_page():

    st.title("RAG PDF Chatbot")

    st.subheader("Login")

    email = st.text_input(
        "Email",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

            return

        try:

            data = login_user(
                email,
                password
            )

            if data.get("success"):

                # =================================
                # Store Access Token
                # =================================

                st.session_state.access_token = (
                    data["access_token"]
                )

                # =================================
                # Store Refresh Token
                # Persist in browser cookie
                # =================================

                st.session_state.refresh_token = (
                    data["refresh_token"]
                )

                cookie_controller.set(
                    "refresh_token",
                    data["refresh_token"],
                    max_age=15 * 24 * 60 * 60
                )

                # =================================
                # Store User Information
                # =================================

                st.session_state.user_id = (
                    data["user_id"]
                )

                st.session_state.user_name = (
                    data["name"]
                )

                st.session_state.user_email = (
                    data["email"]
                )

                # =================================
                # Clear old chat state
                # =================================

                st.session_state.chat_history = []

                st.session_state.active_session_id = None
                st.session_state.active_document_id = None
                st.session_state.active_document_filename = None
                st.session_state.history_loaded_for = None

                st.success(
                    "Login successful."
                )

                st.rerun()

            else:

                st.error(
                    data.get(
                        "message",
                        "Login failed."
                    )
                )

        except Exception:

            st.error(
                "Invalid email or password."
            )


# =========================================
# Register Page
# =========================================

def show_register_page():

    st.title("RAG PDF Chatbot")

    st.subheader("Create Account")

    name = st.text_input(
        "Name",
        key="register_name"
    )

    email = st.text_input(
        "Email",
        key="register_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="register_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="register_confirm_password"
    )

    if st.button(
        "Register",
        use_container_width=True
    ):

        if not name or not email or not password:

            st.warning(
                "Please fill all fields."
            )

            return

        if password != confirm_password:

            st.error(
                "Passwords do not match."
            )

            return

        try:

            data = register_user(
                name,
                email,
                password
            )

            if data.get("success"):

                st.success(
                    "Registration successful. "
                    "Please login."
                )

                st.session_state.show_register = False

                st.rerun()

            else:

                st.error(
                    data.get(
                        "message",
                        "Registration failed."
                    )
                )

        except Exception as e:

            try:

                if (
                    hasattr(e, "response")
                    and e.response is not None
                ):

                    error_data = e.response.json()

                    st.error(
                        error_data.get(
                            "detail",
                            "Unable to register."
                        )
                    )

                else:

                    st.error(
                        "Unable to register."
                    )

            except Exception:

                st.error(
                    "Unable to register."
                )