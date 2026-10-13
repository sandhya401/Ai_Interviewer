
import streamlit as st

from services.dashboard_service import get_dashboard_data


def render_dashboard(user_id=None):
    """Render the AI Interviewer dashboard for the logged-in user."""

    st.title("AI Interviewer Dashboard")
    st.caption("Track your interview practice and progress.")

    data = get_dashboard_data(user_id=user_id)

    if not data.get("ownership_configured", True):
        st.warning(
            "Interview ownership is not configured in the database yet. "
            "Personalized interview history is hidden until this is fixed."
        )
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Interviews",
        data["total_interviews"],
    )

    col2.metric(
        "Completed",
        data["completed_interviews"],
    )

    average = data["average_score"]
    col3.metric(
        "Average Score",
        f"{average:.1f}/100" if average is not None else "—",
    )

    col4.metric(
        "Completion Rate",
        f"{data['completion_rate']:.1f}%",
    )

    st.divider()

    # Score summary
    st.subheader("Score Summary")

    score_col1, score_col2 = st.columns(2)

    best = data["best_score"]
    lowest = data["lowest_score"]

    score_col1.metric(
        "Best Score",
        f"{best:.1f}/100" if best is not None else "—",
    )

    score_col2.metric(
        "Lowest Score",
        f"{lowest:.1f}/100" if lowest is not None else "—",
    )

    # Recent interview history
    st.divider()
    st.subheader("Recent Interviews")

    interviews = data["recent_interviews"]

    if not interviews:
        st.info(
            "No interviews found yet. Start a practice interview "
            "to see your progress here."
        )
        return

    for interview in interviews:
        score = interview["score"]
        score_text = (
            f"{score:.1f}/100"
            if score is not None
            else "Not scored"
        )

        title = (
            f"{interview['title']} — "
            f"{interview['status']} — {score_text}"
        )

        with st.expander(title):
            st.write(f"**Interview ID:** {interview['id']}")
            st.write(f"**Date:** {interview['created_at']}")
            st.write(f"**Status:** {interview['status']}")
            st.write(f"**Score:** {score_text}")

    st.caption(
        "Scores reflect the saved evaluations available in your database."
    )
