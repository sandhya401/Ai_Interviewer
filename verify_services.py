
import ast
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

REQUIRED_FUNCTIONS = {
    "services/auth_service.py": [
        "init_auth_db",
        "register_user",
        "authenticate_user",
    ],
    "services/auth_ui.py": [
        "init_auth_state",
        "render_auth_page",
        "render_logout_button",
    ],
    "services/dashboard_ui.py": [
        "render_dashboard",
    ],
    "services/question_generator.py": [
        "generate_questions",
    ],
    "services/answer_evaluator.py": [
        "evaluate_answer",
    ],
    "services/interview_controls.py": [
        "prepare_questions",
        "create_interview_state",
    ],
    "services/interview_ui.py": [
        "render_interview_ui",
    ],
    "services/interview_setup_ui.py": [
        "render_interview_setup_ui",
    ],
    "services/resume_ui.py": [
        "render_resume_ui",
    ],
    "services/knowledge_ui.py": [
        "render_knowledge_ui",
    ],
    "services/report_ui.py": [
        "render_report_ui",
    ],
    "services/pdf_report_generator.py": [
        "generate_interview_pdf",
    ],
}


def check_functions():
    errors = []

    print("\nChecking required service functions...\n")

    for relative_path, expected_functions in REQUIRED_FUNCTIONS.items():
        path = PROJECT_ROOT / relative_path

        if not path.is_file():
            message = f"Missing file: {relative_path}"
            print(f"[MISSING] {message}")
            errors.append(message)
            continue

        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
            )
        except (SyntaxError, OSError, UnicodeDecodeError) as exc:
            message = f"Cannot inspect {relative_path}: {exc}"
            print(f"[ERROR] {message}")
            errors.append(message)
            continue

        found = {
            node.name
            for node in ast.walk(tree)
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
        }

        for function_name in expected_functions:
            if function_name in found:
                print(f"[OK] {relative_path}: {function_name}")
            else:
                message = (
                    f"Missing function {function_name} "
                    f"in {relative_path}"
                )
                print(f"[MISSING] {message}")
                errors.append(message)

    return errors


def check_import_discovery():
    print("\nChecking whether key modules can be discovered...\n")
    errors = []

    module_names = [
        "streamlit",
        "sqlalchemy",
        "langchain_ollama",
        "langchain_chroma",
        "chromadb",
        "pypdf",
        "docx",
        "reportlab",
    ]

    for module_name in module_names:
        try:
            available = importlib.util.find_spec(module_name) is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            available = False

        if available:
            print(f"[OK] {module_name}")
        else:
            print(f"[NOT FOUND] {module_name}")
            errors.append(f"Dependency not found: {module_name}")

    return errors


def main():
    print("=" * 60)
    print("AI INTERVIEWER - SERVICE COMPATIBILITY CHECK")
    print("=" * 60)

    function_errors = check_functions()
    dependency_errors = check_import_discovery()

    print("\nSummary")
    print(f"Function/file issues: {len(function_errors)}")
    print(f"Dependency issues:    {len(dependency_errors)}")

    if function_errors or dependency_errors:
        print("\nRESULT: FIX THE REPORTED ISSUES FIRST.")
    else:
        print(
            "\nRESULT: BASIC SERVICE CHECKS PASSED. "
            "Function arguments and runtime behavior still need testing."
        )


if __name__ == "__main__":
    main()
