
from typing import List, Optional

from pydantic import BaseModel, Field


class AnswerEvaluation(BaseModel):
    correctness_score: int = Field(
        ge=0, le=10,
        description="Technical or factual correctness."
    )

    depth_score: int = Field(
        ge=0, le=10,
        description="Depth of understanding."
    )

    example_score: int = Field(
        ge=0, le=10,
        description="Quality of examples or practical application."
    )

    clarity_score: int = Field(
        ge=0, le=10,
        description="Clarity, relevance, and organization."
    )

    strengths: List[str] = Field(
        min_length=1,
        description="Specific things the candidate did well."
    )

    improvement_areas: List[str] = Field(
        min_length=1,
        description="Specific gaps or improvements needed."
    )

    feedback: str = Field(
        description="Constructive explanation of the evaluation."
    )

    ideal_answer: str = Field(
        description="A technically accurate model answer for learning."
    )

    follow_up_question: Optional[str] = Field(
        default=None,
        description=(
            "One relevant follow-up question based on the "
            "candidate's answer, or null if not requested."
        )
    )
