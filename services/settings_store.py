
from interview_settings import InterviewSettings


def build_interview_settings(
    difficulty: str = "Intermediate",
    question_time_limit: int = 120,
    total_time_limit: int = 1800,
    randomize_questions: bool = True,
    voice_input_enabled: bool = False,
    voice_output_enabled: bool = False,
):
    settings = InterviewSettings(
        difficulty=difficulty,
        question_time_limit=question_time_limit,
        total_time_limit=total_time_limit,
        randomize_questions=randomize_questions,
        voice_input_enabled=voice_input_enabled,
        voice_output_enabled=voice_output_enabled,
    )

    return settings.to_dict()
