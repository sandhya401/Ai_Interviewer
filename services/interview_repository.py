
from datetime import datetime, timezone
from typing import Any, Dict, List

from database import SessionLocal
from models import (
    Candidate,
    InterviewSession,
    InterviewQuestionRecord,
    InterviewReport,
)


def _value(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    if hasattr(obj, "model_dump"):
        return obj.model_dump().get(key, default)

    if hasattr(obj, "dict"):
        return obj.dict().get(key, default)

    return getattr(obj, key, default)


def create_interview(
    candidate_name: str,
    config: Dict[str, Any],
    questions: List[Any],
    email: str = None,
    user_id: int = None,
) -> int:
    """Create a candidate and interview with its generated questions."""

    with SessionLocal() as db:
        candidate = Candidate(
            name=candidate_name.strip(),
            email=email.strip() if email else None,
        )
        db.add(candidate)
        db.flush()

        interview = InterviewSession(
            candidate_id=candidate.id,
            user_id=user_id,
            role=config["role"],
            domain=config["domain"],
            experience=str(config["experience"]),
            difficulty=config["difficulty"],
            interview_types=(
                list(config["interview_type"])
                if isinstance(config["interview_type"], (list, tuple))
                else [config["interview_type"]]
            ),
            status="in_progress",
        )
        db.add(interview)
        db.flush()

        for position, question in enumerate(questions):
            db.add(
                InterviewQuestionRecord(
                    interview_id=interview.id,
                    position=position,
                    question=_value(question, "question", ""),
                    question_type=_value(
                        question,
                        "question_type",
                        _value(question, "category", "technical"),
                    ),
                    topic=_value(
                        question,
                        "topic",
                        ", ".join(_value(question, "expected_topics", []))
                        or "General",
                    ),
                    difficulty=_value(
                        question, "difficulty", config["difficulty"]
                    ),
                    evaluation_criteria=_value(
                        question,
                        "evaluation_criteria",
                        _value(question, "expected_topics", []),
                    ),
                )
            )

        db.commit()
        return interview.id


def list_interviews(
    limit: int = 50,
    user_id: int = None,
) -> List[Dict[str, Any]]:
    """Return recent interviews, scoped to the authenticated owner."""

    with SessionLocal() as db:
        query = db.query(InterviewSession)
        if user_id is not None:
            query = query.filter(InterviewSession.user_id == user_id)
        rows = query.order_by(
            InterviewSession.started_at.desc()
        ).limit(max(1, min(limit, 200))).all()

        return [
            {
                "interview_id": row.id,
                "candidate_id": row.candidate_id,
                "role": row.role,
                "domain": row.domain,
                "status": row.status,
                "overall_score": row.overall_score,
                "started_at": (
                    row.started_at.isoformat()
                    if row.started_at else None
                ),
            }
            for row in rows
        ]


def complete_interview(
    interview_id: int,
    report: Dict[str, Any],
    user_id: int = None,
) -> None:
    """Mark an interview complete and store its final report."""
    with SessionLocal() as db:
        query = db.query(InterviewSession).filter_by(id=interview_id)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        interview = query.first()

        if interview is None:
            raise ValueError("Interview not found.")

        interview.status = "completed"
        interview.overall_score = report.get("overall_score")
        interview.performance_level = report.get("performance_level")
        interview.completed_at = datetime.now(timezone.utc)
        interview.final_report = report

        stored_report = db.query(InterviewReport).filter_by(
            interview_id=interview_id
        ).first()
        if stored_report is None:
            db.add(InterviewReport(
                interview_id=interview_id,
                report_json=report,
            ))
        else:
            stored_report.report_json = report

        db.commit()


def get_latest_completed_report(user_id: int) -> Dict[str, Any] | None:
    """Load the latest saved report belonging to an authenticated user."""
    with SessionLocal() as db:
        interview = (
            db.query(InterviewSession)
            .filter(
                InterviewSession.user_id == user_id,
                InterviewSession.status == "completed",
            )
            .order_by(InterviewSession.completed_at.desc())
            .first()
        )
        if interview is None:
            return None

        report = interview.final_report
        if not report:
            stored_report = db.query(InterviewReport).filter_by(
                interview_id=interview.id
            ).first()
            report = stored_report.report_json if stored_report else None

        if not report:
            return None

        return {
            "report": report,
            "interview_id": interview.id,
            "role": interview.role,
            "candidate_name": interview.candidate.name,
        }
