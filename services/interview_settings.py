
from typing import Literal

from pydantic import BaseModel, Field


class InterviewSettings(BaseModel):
    """Configuration selected before starting an interview."""

    role: str = Field(default="Python Developer", min_length=1)
    experience_level: Literal[
        "Fresher",
        "Junior",
        "Mid-Level",
        "Senior",
    ] = "Junior"
    num_questions: int = Field(default=5, ge=1, le=50)
    difficulty: Literal["Easy", "Medium", "Hard", "Mixed"] = "Mixed"
    interview_type: Literal[
        "Technical",
        "Behavioral",
        "HR",
        "Mixed",
    ] = "Technical"
    job_description: str = ""
    resume_text: str = ""
    adaptive_mode: bool = True
    voice_mode: bool = False
    question_time_limit: int = Field(default=120, ge=15, le=1800)
    total_time_limit: int = Field(default=1200, ge=60, le=7200)
    randomize_questions: bool = True
    voice_input_enabled: bool = False
    voice_output_enabled: bool = False
