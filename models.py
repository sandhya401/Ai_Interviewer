
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Column,
)
from sqlalchemy.orm import relationship

from database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    interviews = relationship(
        "InterviewSession",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(
        Integer, ForeignKey("candidates.id"), nullable=False, index=True
    )
    user_id = Column(Integer, nullable=True, index=True)
    role = Column(String(150), nullable=False)
    domain = Column(String(200), nullable=False)
    experience = Column(String(100), nullable=False)
    difficulty = Column(String(30), nullable=False)
    interview_types = Column(JSON, nullable=False)
    status = Column(String(30), default="in_progress")
    overall_score = Column(Float, nullable=True)
    performance_level = Column(String(50), nullable=True)
    started_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    final_report = Column(JSON, nullable=True)

    candidate = relationship("Candidate", back_populates="interviews")
    questions = relationship(
        "InterviewQuestionRecord",
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="InterviewQuestionRecord.position",
    )


class InterviewQuestionRecord(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True)
    interview_id = Column(
        Integer, ForeignKey("interview_sessions.id"), nullable=False, index=True
    )
    position = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    topic = Column(String(200), nullable=False)
    difficulty = Column(String(30), nullable=False)
    evaluation_criteria = Column(JSON, nullable=True)

    interview = relationship("InterviewSession", back_populates="questions")
    answer = relationship(
        "InterviewAnswer",
        back_populates="question_record",
        uselist=False,
        cascade="all, delete-orphan",
    )


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(
        Integer, ForeignKey("interview_questions.id"), nullable=False, unique=True
    )
    answer_text = Column(Text, nullable=False, default="")
    correctness_score = Column(Integer, nullable=True)
    depth_score = Column(Integer, nullable=True)
    example_score = Column(Integer, nullable=True)
    clarity_score = Column(Integer, nullable=True)
    answer_score = Column(Float, nullable=True)
    evaluation = Column(JSON, nullable=True)
    followup_answer = Column(Text, nullable=True)
    followup_evaluation = Column(JSON, nullable=True)
    adaptive_decision = Column(JSON, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)

    question_record = relationship(
        "InterviewQuestionRecord",
        back_populates="answer",
    )


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True)
    interview_id = Column(
        Integer, ForeignKey("interview_sessions.id"), nullable=False, unique=True
    )
    report_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
