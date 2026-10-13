
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FOLDERS = [
    "services",
    "tests",
    "data",
    "knowledge_base",
]

REQUIRED_FILES = [
    "app.py",
    "config.py",
    ".env",
    "requirements.txt",
    "database.py",
    "models.py",
]


def main():
    problems = []

    print("AI Interviewer — Configuration Audit")
    print("=" * 42)

    # Check required files.
    for filename in REQUIRED_FILES:
        path = ROOT / filename

        if path.is_file():
            print(f"[OK] File exists: {filename}")
        else:
            print(f"[MISSING] File: {filename}")
            problems.append(f"Missing file: {filename}")

    # Check folders.
    for folder in REQUIRED_FOLDERS:
        path = ROOT / folder

        if path.is_dir():
            print(f"[OK] Folder exists: {folder}")
        else:
            print(f"[MISSING] Folder: {folder}")
            problems.append(f"Missing folder: {folder}")

    # Read .env without printing its contents.
    env_file = ROOT / ".env"

    if env_file.is_file():
        try:
            from dotenv import dotenv_values

            values = dotenv_values(env_file)

            required_keys = [
                "OLLAMA_BASE_URL",
                "OLLAMA_MODEL",
            ]

            for key in required_keys:
                value = values.get(key)

                if value and str(value).strip():
                    print(f"[OK] .env contains {key}")
                else:
                    print(f"[MISSING] .env value: {key}")
                    problems.append(f"Missing .env value: {key}")

        except ImportError:
            print("[WARNING] python-dotenv is not installed.")
    else:
        print("[WARNING] .env file is absent.")

    # Do not print secret values.
    if os.environ.get("OPENAI_API_KEY"):
        print(
            "[INFO] OPENAI_API_KEY is set in the environment. "
            "This project can still be configured for local Ollama."
        )

    print("\nAudit summary")
    print("-" * 42)

    if problems:
        print(f"Found {len(problems)} issue(s).")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Required files, folders, and configuration keys are present.")
    print("Ollama connectivity and application integration are not tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
