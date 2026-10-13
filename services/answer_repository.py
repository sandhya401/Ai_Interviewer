
from datetime import datetime, timezone
from typing import Any, Dict

from database import SessionLocal
from models import InterviewAnswer, InterviewQuestionRecord


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return {}


def save_answer(
    interview_id: int,
    question_position: int,
    answer_text: str,
    evaluation: Any,
    followup_answer: str = None,
    followup_evaluation: Any = None,
    adaptive_decision: Any = None,
) -> None:
    """Save or update an answer and its associated evaluation."""

    evaluation_data = _as_dict(evaluation)
    followup_data = _as_dict(followup_evaluation)
    adaptive_data = _as_dict(adaptive_decision)

    with SessionLocal() as db:
        question = (
            db.query(InterviewQuestionRecord)
            .filter_by(
                interview_id=interview_id,
                position=question_position,
            )
            .first()
        )

        if question is None:
            raise ValueError("Question not found for this interview.")

        answer = (
            db.query(InterviewAnswer)
            .filter_by(question_id=question.id)
            .first()
        )

        if answer is None:
            answer = InterviewAnswer(question_id=question.id)
            db.add(answer)

        answer.answer_text = answer_text or ""
        answer.correctness_score = evaluation_data.get(
            "correctness_score"
        )
        answer.depth_score = evaluation_data.get("depth_score")
        answer.example_score = evaluation_data.get("example_score")
        answer.clarity_score = evaluation_data.get("clarity_score")
        answer.evaluation = evaluation_data or None
        answer.followup_answer = followup_answer
        answer.followup_evaluation = followup_data or None
        answer.adaptive_decision = adaptive_data or None
        answer.evaluated_at = datetime.now(timezone.utc)

        if evaluation_data:
            score = (
                evaluation_data.get("correctness_score", 0) * 4
                + evaluation_data.get("depth_score", 0) * 2.5
                + evaluation_data.get("example_score", 0) * 2
                + evaluation_data.get("clarity_score", 0) * 1.5
            )
            answer.answer_score = round(score, 1)

        db.commit()
