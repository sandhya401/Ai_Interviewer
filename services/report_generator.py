
from collections import defaultdict
from typing import Any, Dict, List


SCORE_WEIGHTS = {
    "correctness_score": 0.40,
    "depth_score": 0.25,
    "example_score": 0.20,
    "clarity_score": 0.15,
}


def _to_dict(value: Any) -> Dict[str, Any]:
    """Convert a Pydantic model or dictionary into a dictionary."""
    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def calculate_question_score(evaluation: Any) -> float:
    """Calculate one answer's weighted score out of 100."""
    data = _to_dict(evaluation)

    score = sum(
        float(data.get(field, 0)) * weight * 10
        for field, weight in SCORE_WEIGHTS.items()
    )

    return round(max(0.0, min(100.0, score)), 1)


def _normalize_evaluations(evaluations: Any) -> List[Dict[str, Any]]:
    """Support evaluations stored as a list or a dictionary."""
    if isinstance(evaluations, dict):
        values = list(evaluations.values())
    elif isinstance(evaluations, list):
        values = evaluations
    else:
        values = []

    return [
        _to_dict(item)
        for item in values
        if item is not None
    ]


def generate_feedback_report(
    questions: Any,
    evaluations: Any,
    followup_evaluations: Any = None,
) -> Dict[str, Any]:
    """
    Build a complete interview report.

    Args:
        questions: List of interview question dictionaries or Pydantic models.
        evaluations: Main-answer evaluations keyed by question index or a list.
        followup_evaluations: Optional follow-up answer evaluations.

    Returns:
        A dictionary containing scores, strengths, improvement areas,
        topic-wise performance, and recommendations.
    """
    normalized_questions = [
        _to_dict(question)
        for question in (questions or [])
    ]

    normalized_evaluations = _normalize_evaluations(evaluations)
    normalized_followups = _normalize_evaluations(
        followup_evaluations or []
    )

    question_by_index = {
        str(index): question
        for index, question in enumerate(normalized_questions)
    }

    # The app normally stores evaluations under string question indexes.
    if isinstance(evaluations, dict):
        evaluation_items = []
        for key, value in evaluations.items():
            if value is not None:
                evaluation_items.append((str(key), _to_dict(value)))
    else:
        evaluation_items = [
            (str(index), evaluation)
            for index, evaluation in enumerate(normalized_evaluations)
        ]

    question_scores = []
    category_totals = defaultdict(list)
    topic_totals = defaultdict(list)
    strengths = []
    improvements = []
    detailed_results = []

    for question_index, evaluation in evaluation_items:
        question = question_by_index.get(question_index, {})

        # Also support integer-like keys.
        if not question and question_index.isdigit():
            question = question_by_index.get(
                str(int(question_index)), {}
            )

        question_text = question.get(
            "question",
            "Interview question",
        )
        question_type = question.get(
            "question_type",
            "Uncategorized",
        )
        topic = question.get("topic", "General")

        score = calculate_question_score(evaluation)
        question_scores.append(score)
        category_totals[str(question_type)].append(score)
        topic_totals[str(topic)].append(score)

        for item in evaluation.get("strengths", []):
            if isinstance(item, str) and item.strip():
                strengths.append(item.strip())

        for item in evaluation.get("improvement_areas", []):
            if isinstance(item, str) and item.strip():
                improvements.append(item.strip())

        detailed_results.append({
            "question_index": question_index,
            "question": question_text,
            "question_type": question_type,
            "topic": topic,
            "score": score,
            "correctness_score": evaluation.get(
                "correctness_score", 0
            ),
            "depth_score": evaluation.get("depth_score", 0),
            "example_score": evaluation.get("example_score", 0),
            "clarity_score": evaluation.get("clarity_score", 0),
            "feedback": evaluation.get("feedback", ""),
            "ideal_answer": evaluation.get("ideal_answer", ""),
        })

    overall_score = (
        round(sum(question_scores) / len(question_scores), 1)
        if question_scores else 0.0
    )

    def average_by_group(grouped_values):
        return {
            name: round(sum(scores) / len(scores), 1)
            for name, scores in sorted(grouped_values.items())
            if scores
        }

    category_scores = average_by_group(category_totals)
    topic_scores = average_by_group(topic_totals)

    if overall_score >= 85:
        performance = "Excellent"
        summary = (
            "You demonstrated strong interview readiness. "
            "Continue practicing advanced questions and explaining "
            "your reasoning clearly."
        )
    elif overall_score >= 70:
        performance = "Good"
        summary = (
            "You have a good foundation. Strengthen the concepts "
            "where your answers were incomplete and practice "
            "explaining real-world examples."
        )
    elif overall_score >= 50:
        performance = "Developing"
        summary = (
            "You understand some of the material, but several areas "
            "need more practice. Review fundamentals and work through "
            "small practical examples."
        )
    else:
        performance = "Needs Improvement"
        summary = (
            "Focus on core concepts first. Study the ideal answers, "
            "practice explaining each concept in your own words, "
            "and repeat the interview after revision."
        )

    weak_topics = [
        topic
        for topic, score in topic_scores.items()
        if score < 70
    ]

    recommendations = []

    if weak_topics:
        recommendations.append(
            "Revise these topics first: " + ", ".join(weak_topics)
        )

    if overall_score < 70:
        recommendations.append(
            "Practice answering questions using a definition, "
            "a practical example, and an explanation of why the "
            "approach works."
        )

    if any(
        item.get("clarity_score", 0) < 6
        for item in normalized_evaluations
    ):
        recommendations.append(
            "Improve answer structure: explain the main idea first, "
            "then add details and a relevant example."
        )

    if not recommendations:
        recommendations.append(
            "Continue with advanced questions, system-design "
            "scenarios, and timed mock interviews."
        )

    # Remove duplicate feedback items while preserving order.
    strengths = list(dict.fromkeys(strengths))
    improvements = list(dict.fromkeys(improvements))

    return {
        "overall_score": overall_score,
        "performance_level": performance,
        "summary": summary,
        "total_questions": len(normalized_questions),
        "evaluated_questions": len(question_scores),
        "category_scores": category_scores,
        "topic_scores": topic_scores,
        "strengths": strengths,
        "improvement_areas": improvements,
        "recommendations": recommendations,
        "question_results": detailed_results,
        "followup_answers_evaluated": len(normalized_followups),
    }
