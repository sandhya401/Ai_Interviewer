
import streamlit as st

from services.auth_service import (
    authenticate_user,
    register_user,
)


def init_auth_state():
    """Initialize authentication-related Streamlit state."""
    if "authenticated_user" not in st.session_state:
        st.session_state.authenticated_user = None


def render_auth_page():
    """
    Render login and registration screens.

    Returns:
        A public user dictionary when logged in.
        None when authentication is required.
    """
    init_auth_state()

    # Return the current session's authenticated user.
    user = st.session_state.authenticated_user

    if user:
        return user

    st.title("AI Interviewer")
    st.caption("Practice interviews, improve your answers, and track progress.")

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    with login_tab:
        st.subheader("Welcome back")

        with st.form("login_form"):
            identifier = st.text_input(
                "Username or email",
                key="login_identifier",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            login_clicked = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if login_clicked:
            if not identifier.strip() or not password:
                st.error("Enter your username/email and password.")
            else:
                user = authenticate_user(identifier, password)

                if user:
                    st.session_state.authenticated_user = user
                    st.rerun()
                else:
                    st.error("Invalid username/email or password.")

    with register_tab:
        st.subheader("Create your account")

        with st.form("register_form"):
            username = st.text_input(
                "Username",
                help="Use 3–30 letters, numbers, dots, underscores, or hyphens.",
                key="register_username",
            )

            email = st.text_input(
                "Email address",
                key="register_email",
            )

            new_password = st.text_input(
                "Password",
                type="password",
                help="Use at least 10 characters, including a letter and a number.",
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="register_confirm_password",
            )

            register_clicked = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

        if register_clicked:
            if new_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                success, message = register_user(
                    username=username,
                    email=email,
                    password=new_password,
                )

                if success:
                    st.success(
                        "Account created. Please log in using your credentials."
                    )
                else:
                    st.error(message)

    return None


def render_logout_button():
    """Display a logout button in the sidebar."""
    init_auth_state()

    user = st.session_state.authenticated_user

    if not user:
        return

    st.sidebar.write(
        f"Logged in as **{user['username']}**"
    )

    if st.sidebar.button(
        "Logout",
        use_container_width=True,
    ):
        st.session_state.authenticated_user = None
        st.rerun()
