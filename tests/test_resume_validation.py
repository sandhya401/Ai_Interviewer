
from pathlib import Path

import pytest


MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10 MB
SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def validate_resume_file(file_path):
    """Validate a resume file before parsing it."""

    path = Path(file_path)

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only PDF and DOCX files are supported.")

    if not path.exists() or not path.is_file():
        raise ValueError("Resume file does not exist.")

    if path.stat().st_size > MAX_RESUME_SIZE:
        raise ValueError("Resume file exceeds the 10 MB limit.")

    return True


def test_accepts_pdf(tmp_path):
    resume = tmp_path / "resume.pdf"
    resume.write_bytes(b"sample PDF placeholder")

    assert validate_resume_file(resume)


def test_accepts_docx(tmp_path):
    resume = tmp_path / "resume.docx"
    resume.write_bytes(b"sample DOCX placeholder")

    assert validate_resume_file(resume)


def test_rejects_unsupported_extension(tmp_path):
    resume = tmp_path / "resume.txt"
    resume.write_text("Python developer")

    with pytest.raises(ValueError, match="PDF and DOCX"):
        validate_resume_file(resume)


def test_rejects_missing_file(tmp_path):
    resume = tmp_path / "missing.pdf"

    with pytest.raises(ValueError, match="does not exist"):
        validate_resume_file(resume)


def test_rejects_file_over_size_limit(tmp_path):
    resume = tmp_path / "large.pdf"

    # Sparse file: avoids allocating 10 MB of actual content.
    with resume.open("wb") as file:
        file.truncate(MAX_RESUME_SIZE + 1)

    with pytest.raises(ValueError, match="10 MB"):
        validate_resume_file(resume)
