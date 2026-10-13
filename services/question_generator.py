
"""
AI Interviewer - Question Generator

Generates interview questions using a local Ollama model.
Default model: qwen2.5:3b

Dependencies:
    pip install langchain-ollama pydantic

Expected environment variables:
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_CHAT_MODEL=qwen2.5:3b
"""

import json
import logging
import os
import re
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from logger_config import get_logger


logger = get_logger(__name__)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", OLLAMA_MODEL)


# ---------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------

class InterviewQuestion(BaseModel):
    """One interview question."""

    question: str = Field(
        ...,
        min_length=5,
        description="The interview question",
    )

    category: Literal[
        "technical",
        "behavioral",
        "hr",
        "situational",
        "project",
    ] = "technical"

    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ] = "medium"

    expected_topics: List[str] = Field(
        default_factory=list,
        description="Topics expected in a good answer",
    )

    ideal_answer: Optional[str] = None

    follow_up_questions: List[str] = Field(
        default_factory=list,
    )


class QuestionGenerationResult(BaseModel):
    """Result returned by the question generator."""

    role: str
    questions: List[InterviewQuestion]
    total_questions: int


# ---------------------------------------------------------
# Ollama model factory
# ---------------------------------------------------------

def get_llm():
    """
    Create and return the local Ollama chat model.

    This function is also imported by answer_evaluator.py.
    """
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:
        raise ImportError(
            "langchain-ollama is not installed. Run: "
            "pip install langchain-ollama"
        ) from exc

    return ChatOllama(
        model=OLLAMA_CHAT_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
    )


# ---------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------

def _build_question_prompt(
    role: str,
    experience_level: str,
    num_questions: int,
    difficulty: str,
    interview_type: str,
    job_description: str = "",
    resume_text: str = "",
    previous_questions: Optional[List[str]] = None,
) -> str:
    """Build the prompt used to generate interview questions."""

    previous_questions = previous_questions or []

    previous_text = (
        "\n".join(f"- {q}" for q in previous_questions)
        if previous_questions
        else "None"
    )

    job_description = job_description.strip() or "Not provided"
    resume_text = resume_text.strip() or "Not provided"

    return f"""
You are an experienced technical interviewer.

Generate exactly {num_questions} distinct interview questions.

Candidate role: {role}
Experience level: {experience_level}
Requested difficulty: {difficulty}
Interview type: {interview_type}

Job description:
{job_description}

Resume information:
{resume_text}

Questions already asked; do not repeat them:
{previous_text}

Requirements:
1. Match the candidate's role and experience level.
2. Use clear, natural, professional language.
3. Avoid duplicate or nearly identical questions.
4. For technical interviews, test practical knowledge and problem-solving.
5. For behavioral interviews, use realistic workplace situations.
6. For HR interviews, cover communication, motivation, and career goals.
7. For mixed interviews, include a balanced selection of categories.
8. Do not assume the candidate has experience not present in the resume.
9. Provide a short ideal answer or answer outline where appropriate.
10. Include useful evaluation topics for every question.
11. Return valid JSON only, without Markdown fences.

Use this exact JSON structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "category": "technical",
      "difficulty": "medium",
      "expected_topics": [
        "Topic one",
        "Topic two"
      ],
      "ideal_answer": "A concise outline of a strong answer",
      "follow_up_questions": [
        "A relevant follow-up question"
      ]
    }}
  ]
}}

Allowed categories:
technical, behavioral, hr, situational, project

Allowed difficulty values:
easy, medium, hard

Generate exactly {num_questions} questions.
"""


# ---------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------

def _extract_json(text: str) -> dict:
    """Extract a JSON object from model output."""

    if not text or not text.strip():
        raise ValueError("The model returned an empty response.")

    cleaned = text.strip()

    # Remove Markdown code fences if the model adds them.
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Attempt to locate the first JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end <= start:
        raise ValueError(
            "Could not find a JSON object in the model response."
        )

    try:
        result = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"The model returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("Expected a JSON object.")

    return result


def _normalize_question(item: dict) -> dict:
    """Normalize model output before Pydantic validation."""

    if not isinstance(item, dict):
        raise ValueError("Each question must be a JSON object.")

    category_aliases = {
        "technical": "technical",
        "behavioral": "behavioral",
        "behavioural": "behavioral",
        "hr": "hr",
        "situational": "situational",
        "scenario": "situational",
        "project": "project",
    }

    difficulty_aliases = {
        "easy": "easy",
        "beginner": "easy",
        "medium": "medium",
        "moderate": "medium",
        "intermediate": "medium",
        "hard": "hard",
        "difficult": "hard",
        "advanced": "hard",
    }

    raw_category = str(
        item.get("category", "technical")
    ).strip().lower()

    raw_difficulty = str(
        item.get("difficulty", "medium")
    ).strip().lower()

    item["category"] = category_aliases.get(
        raw_category,
        "technical",
    )

    item["difficulty"] = difficulty_aliases.get(
        raw_difficulty,
        "medium",
    )

    # Ensure list-valued fields have the expected type.
    for field_name in (
        "expected_topics",
        "follow_up_questions",
    ):
        value = item.get(field_name, [])

        if isinstance(value, str):
            value = [value] if value.strip() else []

        if not isinstance(value, list):
            value = []

        item[field_name] = [
            str(value_item).strip()
            for value_item in value
            if str(value_item).strip()
        ]

    return item


# ---------------------------------------------------------
# Main question-generation function
# ---------------------------------------------------------

def generate_questions(
    role: str = "Python Developer",
    experience_level: str = "Junior",
    num_questions: int = 5,
    difficulty: str = "Mixed",
    interview_type: str = "Technical",
    job_description: str = "",
    resume_text: str = "",
    previous_questions: Optional[List[str]] = None,
    **kwargs,
) -> List[InterviewQuestion]:
    """
    Generate interview questions using Ollama.

    Args:
        role: Target job role.
        experience_level: Fresher, Junior, Mid-Level, or Senior.
        num_questions: Number of questions to generate.
        difficulty: Easy, Medium, Hard, or Mixed.
        interview_type: Technical, Behavioral, HR, or Mixed.
        job_description: Optional job description.
        resume_text: Optional extracted resume text.
        previous_questions: Questions to avoid repeating.
        **kwargs: Accepts additional optional arguments for
            compatibility with callers.

    Returns:
        A list of InterviewQuestion objects.

    Raises:
        ValueError: If the settings or model response are invalid.
        RuntimeError: If Ollama fails to generate questions.
    """

    role = str(role).strip()

    if not role:
        raise ValueError("Role cannot be empty.")

    try:
        num_questions = int(num_questions)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "num_questions must be an integer."
        ) from exc

    if not 1 <= num_questions <= 50:
        raise ValueError(
            "num_questions must be between 1 and 50."
        )

    if "job_description" in kwargs and not job_description:
        job_description = kwargs["job_description"]

    if "resume_text" in kwargs and not resume_text:
        resume_text = kwargs["resume_text"]

    logger.info(
        "Generating %s questions for role=%s, type=%s",
        num_questions,
        role,
        interview_type,
    )

    prompt = _build_question_prompt(
        role=role,
        experience_level=experience_level,
        num_questions=num_questions,
        difficulty=difficulty,
        interview_type=interview_type,
        job_description=job_description,
        resume_text=resume_text,
        previous_questions=previous_questions,
    )

    try:
        llm = get_llm()
        response = llm.invoke(prompt)

        # LangChain chat models typically return an AIMessage.
        response_text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        if not isinstance(response_text, str):
            response_text = str(response_text)

        parsed = _extract_json(response_text)

        raw_questions = parsed.get("questions", [])

        if not isinstance(raw_questions, list):
            raise ValueError(
                "The model response must contain a questions list."
            )

        questions = []

        for item in raw_questions:
            try:
                normalized = _normalize_question(item)
                questions.append(
                    InterviewQuestion(**normalized)
                )
            except (ValidationError, ValueError, TypeError) as exc:
                logger.warning(
                    "Skipping invalid generated question: %s",
                    exc,
                )

        if not questions:
            raise ValueError(
                "The model did not return any valid questions."
            )

        # Keep the number of questions within the requested limit.
        questions = questions[:num_questions]

        logger.info(
            "Successfully generated %s questions",
            len(questions),
        )

        return questions

    except Exception as exc:
        logger.exception("Question generation failed")

        raise RuntimeError(
            "Failed to generate interview questions. "
            "Check that Ollama is running, the configured model "
            "is installed, and the model returned valid JSON. "
            f"Details: {exc}"
        ) from exc


# ---------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------

def generate_question_texts(
    role: str = "Python Developer",
    num_questions: int = 5,
    **kwargs,
) -> List[str]:
    """Return questions as plain strings."""

    questions = generate_questions(
        role=role,
        num_questions=num_questions,
        **kwargs,
    )

    return [question.question for question in questions]


def generate_questions_dict(
    role: str = "Python Developer",
    num_questions: int = 5,
    **kwargs,
) -> List[dict]:
    """Return questions as dictionaries."""

    questions = generate_questions(
        role=role,
        num_questions=num_questions,
        **kwargs,
    )

    return [
        question.model_dump()
        if hasattr(question, "model_dump")
        else question.dict()
        for question in questions
    ]


def check_ollama_connection() -> bool:
    """Return True if the configured Ollama model can respond."""

    try:
        llm = get_llm()
        response = llm.invoke(
            "Reply with the single word OK."
        )

        content = getattr(response, "content", str(response))

        logger.info(
            "Ollama connection successful: %s",
            str(content)[:100],
        )

        return True

    except Exception:
        logger.exception("Ollama connection check failed")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Checking Ollama connection...")

    if not check_ollama_connection():
        raise SystemExit(
            "Ollama is unavailable. Start Ollama and check your model."
        )

    print("Generating sample interview questions...")

    try:
        generated = generate_questions(
            role="Python Developer",
            experience_level="Junior",
            num_questions=5,
            difficulty="Mixed",
            interview_type="Technical",
        )

        for index, question in enumerate(generated, start=1):
            print(f"\n{index}. {question.question}")
            print(f"   Category: {question.category}")
            print(f"   Difficulty: {question.difficulty}")

    except Exception as exc:
        raise SystemExit(str(exc))
