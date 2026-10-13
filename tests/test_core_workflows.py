
from unittest.mock import patch, MagicMock

import pytest


def test_question_generator_returns_questions():
    """Verify that question generation returns a non-empty question set."""

    from services.question_generator import generate_questions

    fake_question = MagicMock()
    fake_question.question = "What is a Python decorator?"

    fake_result = MagicMock()
    fake_result.questions = [fake_question]

    with patch(
        "services.question_generator.ChatOllama"
    ) as mock_ollama:
        mock_llm = mock_ollama.return_value
        mock_llm.with_structured_output.return_value.invoke.return_value = (
            fake_result
        )

        result = generate_questions(
            role="Python Developer",
            experience="1–3 years",
            categories=["Technical"],
            difficulty="medium",
            number_of_questions=1,
        )

    assert result is not None
    assert len(result.questions) >= 1


def test_answer_evaluator_returns_result():
    """Verify that the evaluator produces an evaluation object."""

    from services.answer_evaluator import evaluate_answer

    with patch(
        "services.answer_evaluator.ChatOllama"
    ) as mock_ollama:
        fake_result = MagicMock()
        fake_result.correctness = 8
        fake_result.depth = 7
        fake_result.examples = 6
        fake_result.clarity = 8
        fake_result.feedback = "Good explanation."

        mock_llm = mock_ollama.return_value
        mock_llm.with_structured_output.return_value.invoke.return_value = (
            fake_result
        )

        result = evaluate_answer(
            question="What is a Python decorator?",
            answer="A decorator modifies a function's behavior.",
        )

    assert result is not None
    assert getattr(result, "correctness", None) == 8


def test_pdf_report_returns_bytes():
    """Verify that PDF export returns PDF bytes."""

    from services.pdf_report_generator import generate_interview_pdf

    report = {
        "overall_score": 80,
        "strengths": ["Good communication"],
        "improvement_areas": ["More examples"],
        "recommendations": ["Practice technical questions"],
    }

    pdf_bytes = generate_interview_pdf(
        report=report,
        candidate_name="Test Candidate",
        role="Python Developer",
    )

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")


def test_interview_settings_validate():
    """Verify the interview settings reject invalid values."""

    from interview_settings import InterviewSettings

    settings = InterviewSettings(
        difficulty="medium",
        question_time_limit=120,
        total_time_limit=1200,
        randomize_questions=False,
        voice_input_enabled=False,
        voice_output_enabled=False,
    )

    assert settings.question_time_limit == 120
    assert settings.total_time_limit == 1200
