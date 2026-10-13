
from typing import List, Literal

from pydantic import BaseModel, Field


QuestionType = Literal[
    "technical",
    "HR",
    "scenario-based",
]


Difficulty = Literal[
    "Beginner",
    "Intermediate",
    "Advanced",
]


class InterviewQuestion(BaseModel):
    question: str = Field(
        description="One clear interview question."
    )

    question_type: QuestionType = Field(
        description="Technical, HR, or scenario-based."
    )

    topic: str = Field(
        description="The skill or concept being assessed."
    )

    difficulty: Difficulty = Field(
        description="The question's difficulty."
    )

    evaluation_criteria: List[str] = Field(
        min_length=2,
        max_length=5,
        description=(
            "Two to five criteria for evaluating the answer."
        ),
    )


class InterviewQuestionSet(BaseModel):
    questions: List[InterviewQuestion] = Field(
        min_length=1,
        max_length=30,
        description="The generated interview questions.",
    )
