
import streamlit as st

from schemas_resume import ResumeAnalysis
from services.interview_repository import create_interview
from services.resume_parser import extract_resume_text
from services.resume_analyzer import analyze_resume
from services.resume_question_generator import generate_resume_questions


def _to_dict(value):
    """Convert a Pydantic model or dictionary to a dictionary."""
    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def _show_list(title, items):
    """Display a list of extracted skills or resume insights."""
    if not items:
        return

    st.markdown(f"#### {title}")

    if isinstance(items, str):
        items = [items]

    for item in items:
        if isinstance(item, dict):
            item = item.get("name", item.get("text", str(item)))

        st.markdown(f"- {item}")


def render_resume_ui(user=None):
    """Render the resume upload and analysis screen."""
    st.title("AI Resume Analyzer")
    st.caption(
        "Analyze your resume locally and generate interview questions "
        "based on your skills and experience."
    )

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        help="Supported formats: PDF and DOCX.",
        key="resume_upload",
    )

    if uploaded_file is None:
        st.info("Upload a resume to begin.")
        return

    # Read the upload into memory.
    resume_bytes = uploaded_file.getvalue()

    # Avoid unexpectedly large uploads.
    if len(resume_bytes) > 10 * 1024 * 1024:
        st.error("The resume file must be 10 MB or smaller.")
        return

    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()

    if extension not in {"pdf", "docx"}:
        st.error("Please upload a PDF or DOCX file.")
        return

    if st.button("Extract and Analyze Resume", type="primary"):
        try:
            with st.spinner("Extracting resume text..."):
                resume_text = extract_resume_text(
                    resume_bytes,
                    uploaded_file.name,
                )

            if not resume_text or not resume_text.strip():
                st.error(
                    "No text was extracted. The file may be scanned or empty."
                )
                return

            # Save extracted text for use across Streamlit reruns.
            st.session_state.resume_text = resume_text
            st.session_state.resume_analysis = None
            st.session_state.resume_questions = None

            with st.spinner("Analyzing your resume with the local LLM..."):
                analysis = analyze_resume(resume_text)

            st.session_state.resume_analysis = _to_dict(analysis)

        except Exception as exc:
            st.error(
                "Resume processing failed. Check the file and local AI "
                f"configuration. Details: {exc}"
            )
            print(f"Resume analysis error: {exc}")
            return

    resume_text = st.session_state.get("resume_text")
    analysis = st.session_state.get("resume_analysis")

    if not resume_text:
        return

    with st.expander("View extracted resume text"):
        st.text_area(
            "Extracted text",
            value=resume_text,
            height=250,
            disabled=True,
        )

    if not analysis:
        return

    st.divider()
    st.subheader("Resume Analysis")

    # Support commonly used schema field names.
    skills = list(analysis.get("skills", []))
    for field in ("programming_languages", "frameworks", "databases", "tools"):
        skills.extend(analysis.get(field, []))
    skills = list(dict.fromkeys(skills))
    experience = analysis.get(
        "total_experience",
        analysis.get("professional_summary", ""),
    )
    education = analysis.get("education", [])
    projects = analysis.get("projects", [])
    missing_skills = analysis.get(
        "missing_skills",
        analysis.get(
            "skills_to_improve",
            analysis.get("missing_or_unclear_information", []),
        ),
    )
    suggestions = analysis.get(
        "suggestions",
        analysis.get(
            "improvement_suggestions",
            analysis.get("potential_interview_topics", []),
        ),
    )
    score = analysis.get(
        "resume_score",
        analysis.get("score"),
    )

    if score is not None:
        st.metric("Resume Score", str(score))

    if experience:
        st.markdown("#### Experience Summary")
        st.write(experience)

    _show_list("Skills", skills)
    _show_list("Education", education)
    _show_list("Projects", projects)
    _show_list("Certifications", analysis.get("certifications", []))
    _show_list("Skills to Improve", missing_skills)
    _show_list("Suggestions", suggestions)

    st.divider()
    st.subheader("Generate Interview Questions")

    role = st.text_input(
        "Target job role",
        value="Python Developer",
        key="resume_target_role",
    )
    domain = st.text_input(
        "Interview domain",
        value="Software development",
        key="resume_target_domain",
    )
    experience = st.selectbox(
        "Experience level",
        ["Beginner", "Intermediate", "Advanced"],
        key="resume_target_experience",
    )
    difficulty = st.selectbox(
        "Question difficulty",
        ["Beginner", "Intermediate", "Advanced"],
        index=1,
        key="resume_target_difficulty",
    )
    question_types = st.multiselect(
        "Question types",
        ["Technical", "HR", "Scenario-based"],
        default=["Technical"],
        key="resume_target_question_types",
    )
    number_of_questions = st.slider(
        "Number of questions",
        min_value=1,
        max_value=15,
        value=5,
        key="resume_target_question_count",
    )

    if st.button(
        "Generate Resume-Based Questions",
        type="primary",
        key="generate_resume_questions",
    ):
        try:
            if not role.strip() or not domain.strip():
                raise ValueError("Enter a target role and interview domain.")
            if not question_types:
                raise ValueError("Select at least one question type.")

            with st.spinner("Generating personalized questions..."):
                analysis_model = ResumeAnalysis.model_validate(analysis)
                question_set = generate_resume_questions(
                    resume_text=resume_text,
                    resume_analysis=analysis_model,
                    role=role.strip(),
                    domain=domain.strip(),
                    experience=experience,
                    difficulty=difficulty,
                    question_types=question_types,
                    number_of_questions=number_of_questions,
                )
                st.session_state.resume_questions = question_set
                st.session_state.resume_question_config = {
                    "role": role.strip(),
                    "domain": domain.strip(),
                    "experience": experience,
                    "difficulty": difficulty,
                    "interview_type": question_types,
                }

        except Exception as exc:
            st.error(f"Could not generate resume-based questions: {exc}")
            print(f"Resume question generation error: {exc}")

    question_set = st.session_state.get("resume_questions")

    if question_set is not None:
        if hasattr(question_set, "model_dump"):
            question_data = question_set.model_dump()
        elif hasattr(question_set, "dict"):
            question_data = question_set.dict()
        elif isinstance(question_set, dict):
            question_data = question_set
        else:
            question_data = {}

        questions = question_data.get("questions", [])

        st.markdown("#### Generated Questions")

        for index, question in enumerate(questions, start=1):
            if isinstance(question, dict):
                question_text = question.get(
                    "question",
                    question.get("question_text", ""),
                )
                category = question.get("category", "General")
                difficulty = question.get("difficulty", "Medium")
            else:
                question_text = getattr(question, "question", str(question))
                category = getattr(question, "category", "General")
                difficulty = getattr(question, "difficulty", "Medium")

            with st.expander(f"Question {index}: {category}"):
                st.write(question_text)
                st.caption(f"Difficulty: {difficulty}")

        st.download_button(
            "Download Generated Questions (JSON)",
            data=__import__("json").dumps(
                question_data,
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            file_name="resume_interview_questions.json",
            mime="application/json",
        )

        if st.button(
            "Use These Questions for an Interview",
            key="use_resume_questions",
        ):
            interview_config = st.session_state.get(
                "resume_question_config",
                {
                    "role": role.strip(),
                    "domain": domain.strip(),
                    "experience": experience,
                    "difficulty": difficulty,
                    "interview_type": question_types,
                },
            )
            interview_id = create_interview(
                candidate_name=(user or {}).get("username", "Candidate"),
                email=(user or {}).get("email"),
                user_id=(user or {}).get("id"),
                config=interview_config,
                questions=questions,
            )
            st.session_state.pending_interview_questions = questions
            st.session_state.interview_questions = questions
            st.session_state.interview_id = interview_id
            st.session_state.interview_role = interview_config["role"]
            st.session_state.interview_answers = {}
            st.session_state.interview_evaluations = {}
            st.session_state.interview_index = 0
            st.session_state.interview_finished = False
            st.session_state.pending_navigation = "Take Interview"
            st.rerun()
