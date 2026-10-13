

from pathlib import Path

from services.resume_parser import extract_resume_text
from services.resume_analyzer import analyze_resume


def main():
    resume_path = Path(input("Enter the PDF or DOCX resume path: ").strip())

    if not resume_path.is_file():
        print("Resume file not found.")
        return

    try:
        resume_text = extract_resume_text(
            resume_path.read_bytes(),
            resume_path.name,
        )

        print("\nResume text extracted successfully.")
        print(f"Characters extracted: {len(resume_text)}")

        analysis = analyze_resume(resume_text)

        print("\nResume analysis:")
        print(analysis.model_dump_json(indent=2))

    except Exception as exc:
        print(f"Resume processing failed: {exc}")


if __name__ == "__main__":
    main()
