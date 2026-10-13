
from services.question_generator import generate_questions


def main():
    config = {
        "role": "Python Developer",
        "domain": "Python and Django",
        "experience": "2–3 years",
        "difficulty": "Intermediate",
        "interview_type": ["Technical", "HR"],
        "number_of_questions": 5,
    }

    result = generate_questions(config)

    print("\nGenerated questions:\n")

    for index, question in enumerate(
        result.questions,
        start=1,
    ):
        print(f"{index}. {question.question}")
        print(f"   Type: {question.question_type}")
        print(f"   Topic: {question.topic}")
        print(f"   Difficulty: {question.difficulty}")
        print(
            "   Criteria: "
            + ", ".join(question.evaluation_criteria)
        )
        print()


if __name__ == "__main__":
    main()
