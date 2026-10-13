
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

# Local Ollama configuration
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b",
)

OLLAMA_EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text",
)

# Storage paths
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
CHROMA_DIR = DATA_DIR / "chroma_db"
DATABASE_PATH = DATA_DIR / "ai_interviewer.db"

# Upload limits
MAX_RESUME_SIZE_MB = 10
MAX_KNOWLEDGE_FILE_SIZE_MB = 10

# Interview defaults
DEFAULT_QUESTION_COUNT = 5
DEFAULT_QUESTION_TIME_SECONDS = 120
DEFAULT_TOTAL_INTERVIEW_SECONDS = 1200

# Create storage directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
