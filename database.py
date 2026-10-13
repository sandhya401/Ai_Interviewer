
import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


# Store the database in a local project directory.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(DATA_DIR / 'ai_interviewer.db').as_posix()}",
)

# SQLite needs this setting for Streamlit's multi-threaded environment.
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()


def init_db():
    """Create database tables defined in models.py."""
    import models  # Register the ORM models with Base.metadata.

    Base.metadata.create_all(bind=engine)

    # create_all does not add columns to existing SQLite databases.
    if DATABASE_URL.startswith("sqlite"):
        columns = {
            column["name"]
            for column in inspect(engine).get_columns("interview_sessions")
        }
        if "user_id" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE interview_sessions "
                        "ADD COLUMN user_id INTEGER"
                    )
                )
            engine.dispose()


def get_db():
    """Provide a database session and always close it."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
