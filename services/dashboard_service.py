
from datetime import datetime
from typing import Any

from sqlalchemy import func, inspect

from database import SessionLocal
from models import InterviewSession


def _get_value(obj: Any, *names: str, default=None):
    """Read the first available attribute from a model."""
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def _is_completed(session_obj) -> bool:
    """Support common status and completion-field names."""
    status = str(
        _get_value(
            session_obj,
            "status",
            "state",
            default="",
        )
        or ""
    ).lower()

    if status in {"completed", "complete", "finished", "submitted"}:
        return True

    completed_at = _get_value(
        session_obj,
        "completed_at",
        "finished_at",
    )
    return completed_at is not None


def _get_score(session_obj):
    """Return a valid score, if one is stored on the session."""
    value = _get_value(
        session_obj,
        "overall_score",
        "average_score",
        "score",
    )

    try:
        score = float(value)
        if 0 <= score <= 100:
            return score
    except (TypeError, ValueError):
        pass

    return None


def _get_date(session_obj):
    """Find a suitable timestamp field."""
    value = _get_value(
        session_obj,
        "created_at",
        "started_at",
        "date_created",
    )

    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="minutes")

    return str(value) if value else "Unknown"


def _get_title(session_obj):
    """Build a readable interview title."""
    return str(
        _get_value(
            session_obj,
            "title",
            "role",
            "job_role",
            "position",
            default="Interview",
        )
        or "Interview"
    )


def _get_owner_id(session_obj):
    """Return the session owner ID, if the model defines one."""
    return _get_value(
        session_obj,
        "user_id",
        "candidate_id",
    )


def _serialize_interview(session_obj):
    return {
        "id": _get_value(session_obj, "id"),
        "title": _get_title(session_obj),
        "status": (
            "Completed"
            if _is_completed(session_obj)
            else "In progress"
        ),
        "score": _get_score(session_obj),
        "created_at": _get_date(session_obj),
    }


def get_dashboard_data(user_id=None, recent_limit=10):
    """
    Return dashboard statistics and recent interviews.

    If user_id is provided, sessions are filtered by the matching
    user_id or candidate_id field, when available on the model.

    Note: user ownership must be configured consistently in the
    InterviewSession model and repository.
    """
    recent_limit = max(1, min(int(recent_limit), 100))

    with SessionLocal() as db:
        # Get mapped columns without assuming a particular model version.
        mapped_columns = {
            column.key
            for column in inspect(InterviewSession).columns
        }

        query = db.query(InterviewSession)

        owner_field = None
        for candidate in ("user_id", "candidate_id"):
            if candidate in mapped_columns:
                owner_field = candidate
                break

        if user_id is not None:
            if owner_field is None:
                # Do not expose everyone’s interview history if ownership
                # has not been added to the model.
                return {
                    "total_interviews": 0,
                    "completed_interviews": 0,
                    "in_progress_interviews": 0,
                    "average_score": None,
                    "best_score": None,
                    "lowest_score": None,
                    "completion_rate": 0.0,
                    "recent_interviews": [],
                    "ownership_configured": False,
                }

            query = query.filter(
                getattr(InterviewSession, owner_field) == user_id
            )

        sessions = query.all()

        serialized = [
            _serialize_interview(item)
            for item in sessions
        ]

        total = len(serialized)
        completed_items = [
            item
            for item in serialized
            if item["status"] == "Completed"
        ]
        in_progress = total - len(completed_items)

        scores = [
            item["score"]
            for item in completed_items
            if item["score"] is not None
        ]

        dated_items = sorted(
            serialized,
            key=lambda item: item["created_at"],
            reverse=True,
        )

        return {
            "total_interviews": total,
            "completed_interviews": len(completed_items),
            "in_progress_interviews": in_progress,
            "average_score": (
                round(sum(scores) / len(scores), 2)
                if scores
                else None
            ),
            "best_score": max(scores) if scores else None,
            "lowest_score": min(scores) if scores else None,
            "completion_rate": (
                round(len(completed_items) / total * 100, 2)
                if total
                else 0.0
            ),
            "recent_interviews": dated_items[:recent_limit],
            "ownership_configured": (
                user_id is None or owner_field is not None
            ),
        }
