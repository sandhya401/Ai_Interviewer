
from services.report_exporter import (
    export_report_to_json,
    save_report_to_json,
)

sample_report = {
    "overall_score": 82.5,
    "performance_level": "Good",
    "strengths": [
        "Understands Python fundamentals",
        "Explains concepts clearly",
    ],
    "improvement_areas": [
        "Practice Django ORM optimization",
    ],
    "recommendations": [
        "Practice database query optimization",
    ],
}

# Create JSON text for a future Streamlit download button.
json_text = export_report_to_json(
    sample_report,
    candidate_name="Sandhya",
)
print(json_text)

# Optional: save a copy to the reports/ folder.
saved_path = save_report_to_json(
    sample_report,
    output_directory="reports",
    candidate_name="Sandhya",
)
print("Saved report:", saved_path)
