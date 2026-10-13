
from dataclasses import dataclass


DIFFICULTY_ALIASES = {
    "beginner": "Beginner",
    "easy": "Beginner",
    "intermediate": "Intermediate",
    "medium": "Intermediate",
    "advanced": "Advanced",
    "hard": "Advanced",
}


@dataclass
class InterviewSettings:
    difficulty: str = "Intermediate"
    question_time_limit: int = 120
    total_time_limit: int = 1800
    randomize_questions: bool = True
    voice_input_enabled: bool = False
    voice_output_enabled: bool = False

    def validate(self):
        normalized = DIFFICULTY_ALIASES.get(str(self.difficulty).lower())
        if normalized is None:
            raise ValueError("Invalid interview difficulty.")
        self.difficulty = normalized

        if not 15 <= self.question_time_limit <= 1800:
            raise ValueError(
                "Question time must be between 15 and 1800 seconds."
            )

        if not 60 <= self.total_time_limit <= 7200:
            raise ValueError(
                "Total interview time must be between 60 and 7200 seconds."
            )

        return self

    def to_dict(self):
        self.validate()

        return {
            "difficulty": self.difficulty,
            "question_time_limit": self.question_time_limit,
            "total_time_limit": self.total_time_limit,
            "randomize_questions": self.randomize_questions,
            "voice_input_enabled": self.voice_input_enabled,
            "voice_output_enabled": self.voice_output_enabled,
        }
