
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def export_report_to_json(
    report: Dict[str, Any],
    candidate_name: str = "Candidate",
) -> str:
    """
    Convert an interview report into a downloadable JSON string.
    Does not create a file on disk.
    """

    if not isinstance(report, dict):
        raise TypeError("Report must be a dictionary.")

    export_data = {
        "candidate_name": candidate_name.strip() or "Candidate",
        "generated_at": datetime.now().astimezone().isoformat(),
        "report": report,
    }

    return json.dumps(
        export_data,
        indent=4,
        ensure_ascii=False,
        default=str,
    )


def save_report_to_json(
    report: Dict[str, Any],
    output_directory: str = "reports",
    candidate_name: str = "Candidate",
) -> str:
    """
    Save a report to a JSON file and return its path.
    """

    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(
        char if char.isalnum() or char in ("-", "_") else "_"
        for char in candidate_name.strip()
    ).strip("_")

    if not safe_name:
        safe_name = "Candidate"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_path / f"{safe_name}_interview_report_{timestamp}.json"

    json_content = export_report_to_json(
        report=report,
        candidate_name=candidate_name,
    )

    file_path.write_text(json_content, encoding="utf-8")

    return str(file_path)
