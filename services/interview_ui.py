
import json
import streamlit as st

from services.answer_evaluator import evaluate_answer
from services.answer_repository import save_answer
from services.interview_repository import complete_interview
from services.report_generator import generate_feedback_report


def _get_value(obj, key, default=None):
    """Read a field from either a dictionary or a Pydantic model."""
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _question_text(question):
    return str(
        _get_value(
            question,
            "question",
            _get_value(question, "question_text", ""),
        )
        or ""
    )


def _evaluation_to_dict(evaluation):
    """Convert evaluation results into a serializable dictionary."""
    if hasattr(evaluation, "model_dump"):
        return evaluation.model_dump()

    if hasattr(evaluation, "dict"):
        return evaluation.dict()

    if isinstance(evaluation, dict):
        return evaluation

    return {"feedback": str(evaluation)}


def _render_evaluation(evaluation):
    """Display the evaluation and useful answer feedback."""
    result = _evaluation_to_dict(evaluation)

    score_fields = [
        ("Correctness", "correctness_score"),
        ("Depth", "depth_score"),
        ("Examples", "example_score"),
        ("Clarity", "clarity_score"),
    ]

    columns = st.columns(4)

    for column, (label, key) in zip(columns, score_fields):
        value = result.get(key)

        if value is not None:
            column.metric(label, f"{value}/10")

    if result.get("feedback"):
        st.markdown("#### Feedback")
        st.write(result["feedback"])

    if result.get("strengths"):
        st.markdown("#### Strengths")
        strengths = result["strengths"]

        if isinstance(strengths, str):
            st.write(strengths)
        else:
            for item in strengths:
                st.markdown(f"- {item}")

    if result.get("improvement_areas"):
        st.markdown("#### Areas to improve")

        for item in result["improvement_areas"]:
            st.markdown(f"- {item}")

    if result.get("ideal_answer"):
        with st.expander("View a suggested answer"):
            st.write(result["ideal_answer"])

    if result.get("follow_up_question"):
        st.markdown("#### Suggested follow-up question")
        st.write(result["follow_up_question"])


def initialize_interview_ui():
    """Initialize the UI-specific session state."""
    defaults = {
        "interview_questions": [],
        "interview_answers": {},
        "interview_evaluations": {},
        "interview_index": 0,
        "interview_finished": False,
        "interview_id": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_interview_ui(user):
    """
    Render the interview screen.

    `user` should be the public user dictionary returned by auth_ui.py.
    Question generation and interview creation should be completed by
    the final app integration before this screen is opened.
    """
    initialize_interview_ui()

    questions = st.session_state.interview_questions

    if not questions:
        st.info(
            "No interview questions are loaded yet. Open Interview Setup, "
            "generate questions, then return here to begin."
        )
        return

    if st.session_state.interview_finished:
        st.success("You have finished this interview.")

        if st.button("Return to Dashboard"):
            st.session_state.interview_questions = []
            st.session_state.interview_answers = {}
            st.session_state.interview_evaluations = {}
            st.session_state.interview_index = 0
            st.session_state.interview_finished = False
            st.session_state.interview_id = None
            st.rerun()

        return

    index = st.session_state.interview_index

    if index >= len(questions):
        st.session_state.interview_finished = True
        st.rerun()
        return

    question = questions[index]
    question_text = _question_text(question)

    st.title("Interview in Progress")
    st.progress((index + 1) / len(questions))
    st.caption(f"Question {index + 1} of {len(questions)}")

    category = _get_value(question, "category", "General")
    difficulty = _get_value(question, "difficulty", "Medium")

    st.markdown(f"**Category:** {category}  ·  **Difficulty:** {difficulty}")
    st.subheader(question_text)

    answer_key = f"answer_{index}"

    answer = st.text_area(
        "Your answer",
        value=st.session_state.interview_answers.get(index, ""),
        key=answer_key,
        height=200,
        placeholder="Explain your answer step by step...",
    )

    st.session_state.interview_answers[index] = answer

    existing_evaluation = st.session_state.interview_evaluations.get(index)

    if existing_evaluation:
        with st.container(border=True):
            _render_evaluation(existing_evaluation)

    left, middle, right = st.columns(3)

    with left:
        if st.button(
            "Evaluate Answer",
            disabled=not answer.strip(),
            use_container_width=True,
        ):
            with st.spinner("Evaluating your answer locally..."):
                try:
                    evaluation = evaluate_answer(
                        question=question_text,
                        answer=answer,
                    )

                    st.session_state.interview_evaluations[index] = (
                        _evaluation_to_dict(evaluation)
                    )
                    interview_id = st.session_state.get("interview_id")
                    if interview_id is not None:
                        save_answer(
                            interview_id=interview_id,
                            question_position=index,
                            answer_text=answer,
                            evaluation=evaluation,
                        )

                    st.rerun()

                except Exception as exc:
                    st.error(
                        "Could not evaluate this answer. "
                        "Check the local Ollama service and model configuration."
                    )
                    # Keep technical details in the local terminal/logs.
                    print(f"Answer evaluation error: {exc}")

    with middle:
        if st.button(
            "Previous",
            disabled=index == 0,
            use_container_width=True,
        ):
            st.session_state.interview_index -= 1
            st.rerun()

    with right:
        if index + 1 < len(questions):
            if st.button(
                "Next Question",
                use_container_width=True,
            ):
                st.session_state.interview_index += 1
                st.rerun()
        else:
            if st.button(
                "Finish Interview",
                use_container_width=True,
            ):
                try:
                    report = generate_feedback_report(
                        questions=questions,
                        evaluations=st.session_state.interview_evaluations,
                    )
                    interview_id = st.session_state.get("interview_id")
                    if interview_id is not None:
                        complete_interview(
                            interview_id=interview_id,
                            report=report,
                            user_id=(user or {}).get("id"),
                        )
                    st.session_state.interview_finished = True
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not save the completed interview: {exc}")
