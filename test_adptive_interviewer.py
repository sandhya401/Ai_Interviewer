
from services.adaptive_interviewer import recommend_next_step


question = {
    "question": "What is the difference between a list and a tuple?",
    "topic": "Python collections",
    "question_type": "technical",
    "difficulty": "Intermediate",
}

answer = (
    "A list is mutable, so we can modify it. "
    "A tuple is immutable after creation."
)

evaluation = {
    "correctness_score": 9,
    "depth_score": 8,
    "example_score": 7,
    "clarity_score": 9,
    "feedback": "The key distinction is correct. Examples would improve the answer.",
    "improvement_areas": ["Give a practical example of immutability."],
}

decision = recommend_next_step(
    question=question,
    answer=answer,
    evaluation=evaluation,
    current_difficulty="Intermediate",
)

print(decision.model_dump_json(indent=2))
