
import streamlit as st

from services.interview_controls import create_interview_state, prepare_questions
from services.question_generator import generate_questions
from services.interview_settings import InterviewSettings
from services.interview_repository import create_interview


def _question_text(question):
    """Extract question text from a dictionary or schema object."""
    if isinstance(question, dict):
        return question.get("question", str(question))

    return getattr(question, "question", str(question))


def _question_list(question_set):
    """Convert supported question-set formats to a list."""
    if question_set is None:
        return []

    if isinstance(question_set, list):
        return question_set

    if isinstance(question_set, dict):
        return question_set.get("questions", [])

    return getattr(question_set, "questions", [])


def render_interview_setup_ui(user=None):
    """Render the interview configuration page."""

    st.title("Set Up Your AI Interview")
    st.write(
        "Choose your role, interview categories, difficulty, and time limits."
    )

    with st.form("interview_setup_form"):
        role = st.text_input(
            "Target job role",
            value="Python Developer",
            placeholder="e.g. Python Backend Developer",
        )

        experience = st.selectbox(
            "Experience level",
            options=[
                "Fresher",
                "1–3 years",
                "3–5 years",
                "5+ years",
            ],
            index=1,
        )

        categories = st.multiselect(
            "Question categories",
            options=[
                "Technical",
                "HR",
                "Project-based",
                "Scenario-based",
            ],
            default=["Technical", "HR"],
        )

        difficulty = st.select_slider(
            "Difficulty",
            options=["Easy", "Medium", "Hard"],
            value="Medium",
        )

        number_of_questions = st.slider(
            "Number of questions",
            min_value=3,
            max_value=20,
            value=5,
        )

        question_time_limit = st.slider(
            "Time per question (seconds)",
            min_value=30,
            max_value=300,
            value=120,
            step=30,
        )

        total_time_limit = st.slider(
            "Total interview time (minutes)",
            min_value=5,
            max_value=60,
            value=20,
            step=5,
        )

        randomize_questions = st.checkbox(
            "Randomize question order",
            value=False,
        )

        voice_input_enabled = st.checkbox(
            "Enable voice input (optional)",
            value=False,
        )

        voice_output_enabled = st.checkbox(
            "Enable spoken questions (optional)",
            value=False,
        )

        submitted = st.form_submit_button(
            "Generate Interview Questions",
            type="primary",
        )

    if not submitted:
        return

    if not role.strip():
        st.error("Please enter the target job role.")
        return

    if not categories:
        st.error("Select at least one question category.")
        return

    settings_data = {
        "difficulty": difficulty,
        "question_time_limit": question_time_limit,
        "total_time_limit": total_time_limit * 60,
        "randomize_questions": randomize_questions,
        "voice_input_enabled": voice_input_enabled,
        "voice_output_enabled": voice_output_enabled,
    }

    try:
        settings = InterviewSettings(**settings_data)

        st.session_state.interview_role = role.strip()
        st.session_state.interview_experience = experience
        st.session_state.interview_categories = categories
        st.session_state.interview_settings = settings

        with st.spinner("Generating interview questions with local AI..."):
            question_set = generate_questions(
                role=role.strip(),
                experience_level=experience,
                interview_type=(
                    categories[0] if len(categories) == 1 else "Mixed"
                ),
                difficulty=difficulty,
                num_questions=number_of_questions,
            )

        questions = _question_list(question_set)

        if not questions:
            st.error(
                "The model did not return any questions. "
                "Check the question generator and Ollama configuration."
            )
            return

        # Apply randomization and initialize interview-related state.
        questions = prepare_questions(
            questions,
            randomize=randomize_questions,
        )

        st.session_state.interview_questions = questions
        st.session_state.interview_index = 0
        st.session_state.interview_answers = {}
        st.session_state.interview_evaluations = {}
        st.session_state.interview_finished = False
        st.session_state.pending_interview_questions = questions
        interview_id = create_interview(
            candidate_name=(user or {}).get("username", "Candidate"),
            email=(user or {}).get("email"),
            user_id=(user or {}).get("id"),
            config={
                "role": role.strip(),
                "domain": ", ".join(categories),
                "experience": experience,
                "difficulty": difficulty,
                "interview_type": categories,
            },
            questions=questions,
        )
        st.session_state.interview_id = interview_id

        # Save timer state using the existing controls helper.
        st.session_state.interview_timer_state = create_interview_state(
            questions=questions,
            settings=settings,
            randomize=False,
        )

        st.success(
            f"Generated {len(questions)} questions for {role.strip()}."
        )

        st.subheader("Question preview")

        for index, question in enumerate(questions, start=1):
            st.write(f"**{index}.** {_question_text(question)}")

        st.info("Your interview is ready. Open Take Interview to begin.")

    except Exception as exc:
        st.error(
            "Could not create the interview. Check that Ollama is running "
            "and the configured chat model is installed. "
            f"Details: {exc}"
        )
        print(f"Interview setup error: {exc}")
