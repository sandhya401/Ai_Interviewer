
import pytest
from sqlalchemy import inspect


def test_database_initialization():
    """Check that the database initializes without errors."""

    from database import init_db, engine

    init_db()

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = {
        "candidates",
        "interview_sessions",
        "interview_questions",
        "interview_answers",
        "interview_reports",
    }

    # Report missing tables rather than assuming model names match.
    missing = expected_tables - set(tables)

    assert not missing, (
        f"Missing tables: {sorted(missing)}. "
        f"Actual tables: {sorted(tables)}"
    )


def test_session_factory_exists():
    """Check that the SQLAlchemy session factory is available."""

    from database import SessionLocal

    session = SessionLocal()

    try:
        assert session is not None
    finally:
        session.close()


def test_interview_session_has_ownership_field():
    """Check whether interview records can be associated with a user."""

    from models import InterviewSession

    mapper = inspect(InterviewSession)
    field_names = {column.key for column in mapper.columns}

    ownership_fields = {
        "user_id",
        "candidate_id",
        "owner_id",
    }

    assert field_names & ownership_fields, (
        "InterviewSession has no ownership field. "
        "Add a user_id or candidate_id relationship before "
        "enabling multi-user interview history."
    )
