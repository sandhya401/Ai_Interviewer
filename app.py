
import streamlit as st
from pathlib import Path

from database import init_db

from services.auth_service import init_auth_db
from services.auth_ui import (
    init_auth_state,
    render_auth_page,
    render_logout_button,
)
from services.dashboard_ui import render_dashboard
from services.interview_setup_ui import render_interview_setup_ui
from services.interview_ui import render_interview_ui
from services.resume_ui import render_resume_ui
from services.knowledge_ui import render_knowledge_ui
from services.report_ui import render_report_ui
from services.interview_repository import get_latest_completed_report


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Interviewer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_styles():
    """Load the app's local visual theme."""
    css_path = Path(__file__).resolve().parent / "assets" / "styles.css"
    try:
        css = css_path.read_text(encoding="utf-8")
    except OSError:
        return
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# --------------------------------------------------
# Initialize databases and authentication state
# --------------------------------------------------

@st.cache_resource
def initialize_databases():
    """Initialize the application and authentication databases."""
    init_db()
    init_auth_db()
    return True


def initialize_application():
    initialize_databases()
    init_auth_state()


# --------------------------------------------------
# Navigation
# --------------------------------------------------

def render_navigation():
    """Render the sidebar navigation."""

    st.sidebar.title("🎯 AI Interviewer")

    user = st.session_state.get("authenticated_user")

    if user:
        username = user.get("username", "Candidate")
        st.sidebar.caption(f"Logged in as {username}")

    pages = [
        "Dashboard",
        "Resume Analyzer",
        "Knowledge Base",
        "Interview Setup",
        "Take Interview",
        "Interview Report",
    ]

    requested_page = st.session_state.pop("pending_navigation", None)
    if requested_page in pages:
        st.session_state.app_navigation = requested_page

    selected_page = st.sidebar.radio(
        "Navigation",
        pages,
        key="app_navigation",
    )

    st.sidebar.divider()

    render_logout_button()

    return selected_page


# --------------------------------------------------
# Page routing
# --------------------------------------------------

def render_selected_page(page, user):
    """Render the selected application page."""

    user_id = user.get("id")

    if page == "Dashboard":
        render_dashboard(user_id=user_id)

    elif page == "Resume Analyzer":
        render_resume_ui(user)

    elif page == "Knowledge Base":
        render_knowledge_ui()

    elif page == "Interview Setup":
        render_interview_setup_ui(user)

    elif page == "Take Interview":
        render_interview_ui(user)

    elif page == "Interview Report":
        questions = st.session_state.get(
            "interview_questions",
            [],
        )
        evaluations = st.session_state.get(
            "interview_evaluations",
            {},
        )

        candidate_name = user.get("username", "Candidate")
        saved_report = None
        if not evaluations:
            saved_report = get_latest_completed_report(user_id)
            if saved_report is None:
                st.info(
                    "Complete an interview to view your saved report."
                )
                return

        role = st.session_state.get(
            "interview_role",
            saved_report["role"] if saved_report else "Not specified",
        )
        interview_id = (
            st.session_state.get("interview_id")
            or (saved_report["interview_id"] if saved_report else None)
        )

        render_report_ui(
            questions=questions,
            evaluations=evaluations,
            candidate_name=candidate_name,
            role=role,
            interview_id=interview_id,
            user_id=user_id,
            report_data=(saved_report["report"] if saved_report else None),
        )


# --------------------------------------------------
# Main application
# --------------------------------------------------

def main():
    inject_custom_styles()
    initialize_application()

    st.title("AI Interviewer")
    st.caption(
        "Practice interviews, analyze your resume, and improve "
        "your answers with locally hosted AI."
    )

    # Authentication is required before accessing application pages.
    user = render_auth_page()

    if not user:
        st.info("Log in or create an account to continue.")
        st.stop()

    selected_page = render_navigation()

    try:
        render_selected_page(
            page=selected_page,
            user=user,
        )
    except Exception as exc:
        st.error(
            "This page could not be loaded. Check its service imports "
            "and function signatures during integration."
        )
        print(
            f"Application page error ({selected_page}): {exc}"
        )


if __name__ == "__main__":
    main()
