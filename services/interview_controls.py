
import random
import time
from typing import Any, Dict, List


def prepare_questions(
    questions: List[Any],
    randomize: bool = True,
    seed: int = None,
) -> List[Any]:
    """Return a copied question list, optionally shuffled."""
    result = list(questions)

    if randomize:
        random.Random(seed).shuffle(result)

    return result


def start_timer(
    duration_seconds: int,
) -> float:
    """Return the deadline timestamp for a countdown timer."""
    if duration_seconds <= 0:
        raise ValueError("Timer duration must be positive.")

    return time.time() + duration_seconds


def get_remaining_seconds(deadline: float) -> int:
    """Return seconds remaining, never below zero."""
    return max(0, int(deadline - time.time()))


def format_duration(seconds: int) -> str:
    """Format seconds as HH:MM:SS."""
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def adjust_difficulty(
    current_difficulty: str,
    average_score: float,
) -> str:
    """
    Suggest the next difficulty from a 0-10 evaluation average.
    This is a recommendation; the app decides whether to apply it.
    """
    levels = ["Beginner", "Intermediate", "Advanced"]

    if current_difficulty not in levels:
        raise ValueError("Invalid difficulty.")

    current_index = levels.index(current_difficulty)

    if average_score >= 8 and current_index < 2:
        return levels[current_index + 1]

    if average_score < 5 and current_index > 0:
        return levels[current_index - 1]

    return current_difficulty


def create_interview_state(
    questions: List[Any],
    question_time_limit: int = 120,
    total_time_limit: int = 1200,
    randomize: bool = True,
    settings=None,
) -> Dict[str, Any]:
    """Prepare initial timer and question state for Streamlit."""
    if not questions:
        raise ValueError("At least one interview question is required.")

    if settings is not None:
        question_time_limit = settings.question_time_limit
        total_time_limit = settings.total_time_limit
        randomize = settings.randomize_questions

    if question_time_limit <= 0 or total_time_limit <= 0:
        raise ValueError("Interview time limits must be positive.")

    prepared = prepare_questions(questions, randomize=randomize)
    now = time.time()

    return {
        "questions": prepared,
        "current_index": 0,
        "question_deadline": now + question_time_limit,
        "interview_deadline": now + total_time_limit,
        "question_time_limit": question_time_limit,
        "total_time_limit": total_time_limit,
        "started_at": now,
    }
