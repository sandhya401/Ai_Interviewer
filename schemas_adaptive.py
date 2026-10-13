
from typing import Literal, Optional
from pydantic import BaseModel, Field


class AdaptiveDecision(BaseModel):
    next_action: Literal[
        "advance",
        "probe",
        "simplify",
        "retry",
    ] = Field(description="Recommended next interview action.")

    next_difficulty: Literal[
        "Beginner",
        "Intermediate",
        "Advanced",
    ] = Field(description="Difficulty for the next main question.")

    focus_topic: str = Field(
        description="Concept to test in the next question."
    )

    followup_question: Optional[str] = Field(
        default=None,
        description="One follow-up question, or null if unnecessary.",
    )

    reasoning: str = Field(
        description="Brief explanation for the adaptive decision."
    )
