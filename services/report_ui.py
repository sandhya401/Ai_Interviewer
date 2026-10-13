
import json
import streamlit as st

from services.pdf_report_generator import generate_interview_pdf
from services.report_generator import generate_feedback_report
from services.interview_repository import complete_interview


def _to_dict(value):
    """Convert supported report objects to dictionaries."""
    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {"summary": str(value)}


def render_report_ui(
    questions,
    evaluations,
    candidate_name="Candidate",
    role="Not specified",
    interview_id=None,
    user_id=None,
    report_data=None,
):
    """Render an interview report with PDF and JSON download buttons."""

    st.title("Interview Feedback Report")

    if not evaluations and not report_data:
        st.info("No evaluations are available for this interview yet.")
        return

    try:
        report = report_data or generate_feedback_report(
            questions=questions,
            evaluations=evaluations,
        )
        report = _to_dict(report)
        if (
            report_data is None
            and
            interview_id is not None
            and st.session_state.get("interview_finished", False)
        ):
            complete_interview(
                interview_id=interview_id,
                report=report,
                user_id=user_id,
            )

    except Exception as exc:
        st.error("Unable to generate the interview report.")
        print(f"Report generation error: {exc}")
        return

    st.subheader("Performance Summary")

    score = report.get(
        "overall_score",
        report.get("average_score", report.get("score")),
    )

    if score is not None:
        try:
            st.metric("Overall Score", f"{float(score):.1f}/100")
        except (ValueError, TypeError):
            st.metric("Overall Score", str(score))

    summary = report.get("summary")
    if summary:
        st.write(summary)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Strengths")
        strengths = report.get("strengths", [])

        if isinstance(strengths, str):
            strengths = [strengths]

        if strengths:
            for item in strengths:
                st.markdown(f"- {item}")
        else:
            st.write("No strengths recorded.")

    with col2:
        st.subheader("Areas to Improve")
        improvements = report.get(
            "improvement_areas",
            report.get("areas_for_improvement", []),
        )

        if isinstance(improvements, str):
            improvements = [improvements]

        if improvements:
            for item in improvements:
                st.markdown(f"- {item}")
        else:
            st.write("No improvement areas recorded.")

    recommendations = report.get("recommendations", [])

    if recommendations:
        st.subheader("Recommendations")

        if isinstance(recommendations, str):
            recommendations = [recommendations]

        for item in recommendations:
            st.markdown(f"- {item}")

    st.divider()
    st.subheader("Download Your Report")

    report_payload = {
        **report,
        "candidate_name": candidate_name,
        "role": role,
        "interview_id": interview_id,
    }

    try:
        pdf_bytes = generate_interview_pdf(
            report=report_payload,
            candidate_name=candidate_name,
            role=role,
        )

        json_bytes = json.dumps(
            report_payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

        col1, col2 = st.columns(2)

        safe_id = str(interview_id or "latest")

        with col1:
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"interview_report_{safe_id}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with col2:
            st.download_button(
                label="Download JSON",
                data=json_bytes,
                file_name=f"interview_report_{safe_id}.json",
                mime="application/json",
                use_container_width=True,
            )

    except Exception as exc:
        st.error("Unable to prepare report downloads.")
        print(f"Report export error: {exc}")
