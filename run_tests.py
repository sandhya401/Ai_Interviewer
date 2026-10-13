
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
TESTS_DIR = PROJECT_ROOT / "tests"
REPORT_FILE = PROJECT_ROOT / "test_results.txt"


def main():
    if not TESTS_DIR.exists():
        print(f"ERROR: Tests folder not found: {TESTS_DIR}")
        return 1

    command = [
        sys.executable,
        "-m",
        "pytest",
        str(TESTS_DIR),
        "-v",
        "--tb=short",
    ]

    print("Running AI Interviewer tests...")
    print("The Streamlit application will NOT be launched.")

    try:
        with REPORT_FILE.open("w", encoding="utf-8") as report:
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="replace",
                check=False,
            )

            report.write(result.stdout)
            print(result.stdout)

        print(f"\nTest report saved to: {REPORT_FILE}")
        return result.returncode

    except OSError as exc:
        print(f"Unable to run tests: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
