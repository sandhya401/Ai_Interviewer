
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "app.py",
    "config.py",
    ".env",
    ".gitignore",
    "requirements.txt",
    "database.py",
    "models.py",
    "schemas.py",
    "evaluation_schemas.py",
    "schemas_resume.py",
    "interview_settings.py",
    "init_database.py",
    "logger_config.py",
    "error_handler.py",
    "health_check.py",
    "verify_project.py",
    "verify_imports.py",
    "verify_config.py",
    "verify_dependencies.py",
    "verify_security.py",
    "run_tests.py",
]

REQUIRED_SERVICES = [
    "__init__.py",
    "auth_service.py",
    "auth_ui.py",
    "dashboard_service.py",
    "dashboard_ui.py",
    "question_generator.py",
    "answer_evaluator.py",
    "adaptive_interviewer.py",
    "interview_controls.py",
    "interview_ui.py",
    "interview_setup_ui.py",
    "resume_analyzer.py",
    "resume_question_generator.py",
    "resume_ui.py",
    "rag_service.py",
    "knowledge_ui.py",
    "report_generator.py",
    "report_ui.py",
    "pdf_report_generator.py",
    "interview_repository.py",
    "answer_repository.py",
    "settings_store.py",
    "voice_service.py",
]

REQUIRED_FOLDERS = [
    "services",
    "tests",
    "data",
    "knowledge_base",
]


def main():
    missing = []

    print("AI Interviewer — Structure Audit")
    print("=" * 44)

    for filename in REQUIRED_FILES:
        path = ROOT / filename
        if path.is_file():
            print(f"[OK] {filename}")
        else:
            print(f"[MISSING] {filename}")
            missing.append(filename)

    for filename in REQUIRED_SERVICES:
        path = ROOT / "services" / filename
        if path.is_file():
            print(f"[OK] services/{filename}")
        else:
            print(f"[MISSING] services/{filename}")
            missing.append(f"services/{filename}")

    for folder in REQUIRED_FOLDERS:
        path = ROOT / folder
        if path.is_dir():
            print(f"[OK] {folder}/")
        else:
            print(f"[MISSING] {folder}/")
            missing.append(f"{folder}/")

    print("\nSummary")
    print("-" * 44)

    if missing:
        print(f"{len(missing)} required paths are missing.")
        print("Review the list above before proceeding.")
        return 1

    print("All listed paths exist.")
    print("This confirms structure only, not integration or correctness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
