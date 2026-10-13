
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"(?i)secret[_-]?key\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"][^'\"]+['\"]"),
]

SENSITIVE_FILES = {
    ".env",
    "id_rsa",
    "id_ed25519",
}


def scan_python_files():
    findings = []

    for path in ROOT.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        try:
            lines = path.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()
        except OSError:
            continue

        for line_number, line in enumerate(lines, start=1):
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    # Do not print the matched line; it may contain a secret.
                    findings.append(
                        f"Possible hardcoded secret: "
                        f"{path.relative_to(ROOT)}:{line_number}"
                    )
                    break

    return findings


def main():
    findings = []

    gitignore = ROOT / ".gitignore"

    if not gitignore.exists():
        findings.append("Missing .gitignore")
    else:
        rules = set(
            gitignore.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()
        )

        for rule in (".env", "__pycache__/", "*.pyc"):
            if rule not in rules:
                findings.append(
                    f".gitignore may be missing rule: {rule}"
                )

    for filename in SENSITIVE_FILES:
        if filename == ".env" and (ROOT / filename).exists():
            print(
                "[INFO] .env exists locally. "
                "Keep it out of version control."
            )

    findings.extend(scan_python_files())

    print("\nSecurity audit")
    print("=" * 42)

    if findings:
        for finding in findings:
            print(f"[REVIEW] {finding}")

        print(
            "\nReview findings manually. This simple scanner can "
            "produce false positives and cannot guarantee security."
        )
        return 1

    print("No issues detected by these basic checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    logger.propagate = False

    return logger
