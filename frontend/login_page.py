import streamlit as st

from frontend.api_client import (
    login_user,
    register_user,
    forgot_password,
    reset_password
)


# =========================================
# Helper: Display Backend Error
# =========================================

def display_backend_error(
    exception,
    default_message
):

    try:

        if (
            hasattr(exception, "response")
            and exception.response is not None
        ):

            error_data = exception.response.json()

            detail = error_data.get(
                "detail",
                default_message
            )

            st.error(detail)

        else:

            st.error(default_message)

    except Exception:

        st.error(default_message)


# =========================================
# Login Page
# =========================================

def show_login_page(cookies):

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

    # =========================================
    # Login Button
    # =========================================

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
                # Access Token
                # =================================

                st.session_state.access_token = (
                    data["access_token"]
                )

                # =================================
                # Refresh Token
                # =================================

                refresh_token = data["refresh_token"]

                st.session_state.refresh_token = (
                    refresh_token
                )

                # Save refresh token in browser cookie
                cookies["refresh_token"] = (
                    refresh_token
                )

                cookies.save()

                # =================================
                # User Information
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
                # Clear Old Chat State
                # =================================

                st.session_state.chat_history = []

                st.session_state.active_session_id = None

                st.session_state.active_document_id = None

                st.session_state.active_document_filename = None

                st.session_state.history_loaded_for = None

                # =================================
                # Login Success
                # =================================

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

        except Exception as e:

            # =================================
            # Backend 403 will show:
            # Please verify your email before logging in.
            # =================================

            display_backend_error(
                e,
                "Invalid email or password."
            )


    # =========================================
    # Forgot Password
    # =========================================

    st.markdown("---")

    if st.button(
        "Forgot Password?",
        use_container_width=True
    ):

        st.session_state.show_forgot_password = True

        st.rerun()


# =========================================
# Register Page
# =========================================

def show_register_page():

    # =========================================
    # Registration Success Screen
    # =========================================

    if st.session_state.get(
        "registration_success",
        False
    ):

        st.title("RAG PDF Chatbot")

        st.subheader(
            "Registration Successful"
        )

        st.success(
            "Your account has been created successfully."
        )

        st.info(
            "We've sent a verification link to your email. "
            "Please check your inbox and click the link "
            "to verify your account before logging in."
        )

        st.write(
            "After verifying your email, return here "
            "and login."
        )

        if st.button(
            "Go to Login",
            use_container_width=True
        ):

            st.session_state.registration_success = False

            st.session_state.show_register = False

            st.rerun()

        return


    # =========================================
    # Registration Form
    # =========================================

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

    # =========================================
    # Password Length Hint
    # =========================================

    if password:

        if len(password) < 8:

            st.caption(
                f"Minimum 8 characters "
                f"({len(password)}/8)"
            )

        else:

            st.caption(
                "✓ Password length requirement met"
            )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="register_confirm_password"
    )

    # =========================================
    # Register Button
    # =========================================

    if st.button(
        "Register",
        use_container_width=True
    ):

        # =========================================
        # Validate Fields
        # =========================================

        if not name or not email or not password:

            st.warning(
                "Please fill all fields."
            )

            return

        # =========================================
        # Validate Password Length
        # =========================================

        if len(password) < 8:

            st.error(
                "Password must be at least 8 characters."
            )

            return

        # =========================================
        # Confirm Password
        # =========================================

        if password != confirm_password:

            st.error(
                "Passwords do not match."
            )

            return

        # =========================================
        # Register User
        # =========================================

        try:

            data = register_user(
                name,
                email,
                password
            )

            if data.get("success"):

                # =================================
                # Do NOT immediately open login.
                # =================================

                st.session_state.registration_success = True

                st.rerun()

            else:

                st.error(
                    data.get(
                        "message",
                        "Registration failed."
                    )
                )

        except Exception as e:

            display_backend_error(
                e,
                "Unable to register."
            )


# =========================================
# Forgot Password Page
# =========================================

def show_forgot_password_page():

    st.title("RAG PDF Chatbot")

    st.subheader("Forgot Password")

    st.write(
        "Enter your registered email address and "
        "we'll send you a password reset link."
    )

    email = st.text_input(
        "Email",
        key="forgot_password_email"
    )

    # =========================================
    # Send Reset Link
    # =========================================

    if st.button(
        "Send Reset Link",
        use_container_width=True
    ):

        if not email:

            st.warning(
                "Please enter your email address."
            )

            return

        try:

            data = forgot_password(
                email
            )

            if data.get("success"):

                st.success(
                    data.get(
                        "message",
                        "If an account exists with this email, "
                        "a password reset link has been sent."
                    )
                )

                st.info(
                    "Please check your email and click "
                    "the password reset link."
                )

            else:

                st.error(
                    data.get(
                        "message",
                        "Unable to send reset link."
                    )
                )

        except Exception as e:

            display_backend_error(
                e,
                "Unable to send password reset link."
            )


    # =========================================
    # Back To Login
    # =========================================

    st.markdown("---")

    if st.button(
        "Back to Login",
        use_container_width=True
    ):

        st.session_state.show_forgot_password = False

        st.rerun()


# =========================================
# Reset Password Page
# =========================================

def show_reset_password_page(token):

    st.title("RAG PDF Chatbot")

    st.subheader("Reset Password")

    st.write(
        "Create a new password for your account."
    )

    new_password = st.text_input(
        "New Password",
        type="password",
        key="reset_new_password"
    )

    # =========================================
    # Password Length Hint
    # =========================================

    if new_password:

        if len(new_password) < 8:

            st.caption(
                f"Minimum 8 characters "
                f"({len(new_password)}/8)"
            )

        else:

            st.caption(
                "✓ Password length requirement met"
            )

    confirm_password = st.text_input(
        "Confirm New Password",
        type="password",
        key="reset_confirm_password"
    )

    # =========================================
    # Reset Password
    # =========================================

    if st.button(
        "Reset Password",
        use_container_width=True
    ):

        # =========================================
        # Validate Password
        # =========================================

        if not new_password or not confirm_password:

            st.warning(
                "Please fill both password fields."
            )

            return

        # =========================================
        # Minimum Password Length
        # =========================================

        if len(new_password) < 8:

            st.error(
                "Password must be at least 8 characters."
            )

            return

        # =========================================
        # Confirm Password
        # =========================================

        if new_password != confirm_password:

            st.error(
                "Passwords do not match."
            )

            return

        # =========================================
        # Reset Password API
        # =========================================

        try:

            data = reset_password(
                token,
                new_password
            )

            if data.get("success"):

                st.success(
                    data.get(
                        "message",
                        "Password reset successfully. "
                        "You can now login with your new password."
                    )
                )

                st.session_state.show_reset_password = False

                st.session_state.reset_token = None

                st.info(
                    "You can now login with your new password."
                )

                # =========================================
                # Go To Login
                # =========================================

                if st.button(
                    "Go to Login",
                    use_container_width=True
                ):

                    # Remove reset token from URL
                    st.query_params.clear()

                    st.session_state.show_reset_password = False

                    st.session_state.reset_token = None

                    st.rerun()

            else:

                st.error(
                    data.get(
                        "message",
                        "Unable to reset password."
                    )
                )

        except Exception as e:

            display_backend_error(
                e,
                "Invalid or expired password reset link."
            )


    # =========================================
    # Back To Login
    # =========================================

    st.markdown("---")

    if st.button(
        "Back to Login",
        use_container_width=True
    ):

        st.session_state.show_reset_password = False

        st.session_state.reset_token = None

        # Remove reset token from browser URL
        st.query_params.clear()

        st.rerun()