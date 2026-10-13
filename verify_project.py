
import ast
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "app.py",
    "config.py",
    "database.py",
    "models.py",
    "schemas.py",
    "evaluation_schemas.py",
    "interview_settings.py",
    "services/__init__.py",
    "services/auth_service.py",
    "services/auth_ui.py",
    "services/dashboard_service.py",
    "services/dashboard_ui.py",
    "services/question_generator.py",
    "services/answer_evaluator.py",
    "services/adaptive_interviewer.py",
    "services/interview_controls.py",
    "services/interview_ui.py",
    "services/interview_setup_ui.py",
    "services/resume_ui.py",
    "services/rag_service.py",
    "services/knowledge_ui.py",
    "services/report_generator.py",
    "services/report_ui.py",
    "services/pdf_report_generator.py",
]


def check_required_files():
    print("\n1. Checking required files")
    missing = []

    for relative_path in REQUIRED_FILES:
        path = PROJECT_ROOT / relative_path

        if path.is_file():
            print(f"[OK]      {relative_path}")
        else:
            print(f"[MISSING] {relative_path}")
            missing.append(relative_path)

    return missing


def check_python_syntax():
    print("\n2. Checking Python syntax")
    python_files = sorted(
        path
        for path in PROJECT_ROOT.rglob("*.py")
        if not any(
            part in {
                ".venv",
                "venv",
                "__pycache__",
                ".git",
            }
            for part in path.parts
        )
    )

    errors = []

    for path in python_files:
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
            print(f"[OK]      {path.relative_to(PROJECT_ROOT)}")

        except SyntaxError as exc:
            message = (
                f"{path.relative_to(PROJECT_ROOT)}:"
                f"{exc.lineno}:{exc.offset} - {exc.msg}"
            )
            errors.append(message)
            print(f"[ERROR]   {message}")

        except (OSError, UnicodeDecodeError) as exc:
            message = f"{path.relative_to(PROJECT_ROOT)} - {exc}"
            errors.append(message)
            print(f"[ERROR]   {message}")

    return errors


def main():
    print("=" * 60)
    print("AI INTERVIEWER - PRE-RUN VERIFICATION")
    print("=" * 60)
    print(f"Project directory: {PROJECT_ROOT}")

    missing = check_required_files()
    syntax_errors = check_python_syntax()

    print("\n3. Verification summary")
    print(f"Missing required files: {len(missing)}")
    print(f"Python syntax errors:    {len(syntax_errors)}")

    if missing or syntax_errors:
        print(
            "\nRESULT: NOT READY. Fix the listed problems "
            "before proceeding."
        )
        sys.exit(1)

    print(
        "\nRESULT: BASIC CHECKS PASSED."
        "\nThis does not yet prove that imports, function signatures, "
        "database operations, or AI services work together."
    )


if __name__ == "__main__":
    main()
