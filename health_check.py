
import os
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent


def check_ollama():
    """Check Ollama connectivity and list locally available models."""

    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    ).rstrip("/")

    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    request = Request(
        f"{base_url}/api/tags",
        headers={"Accept": "application/json"},
    )

    try:
        with urlopen(request, timeout=5) as response:
            import json

            data = json.loads(response.read().decode("utf-8"))

        available_models = {
            item.get("name", "")
            for item in data.get("models", [])
        }

        print(f"[OK] Ollama is reachable at {base_url}")

        if model in available_models:
            print(f"[OK] Model is available: {model}")
        elif any(name.split(":")[0] == model.split(":")[0]
                 for name in available_models):
            print(f"[WARNING] Check the configured model tag: {model}")
            print(f"Available models: {sorted(available_models)}")
        else:
            print(f"[MISSING] Model not found: {model}")
            print(f"Available models: {sorted(available_models)}")
            return False

        return True

    except (URLError, TimeoutError, OSError, ValueError) as exc:
        print(f"[FAILED] Ollama health check: {type(exc).__name__}")
        print("Start Ollama and verify OLLAMA_BASE_URL.")
        return False


def main():
    print("AI Interviewer — Local Health Check")
    print("=" * 42)

    required_paths = [
        ROOT / "app.py",
        ROOT / "config.py",
        ROOT / "database.py",
        ROOT / "services",
    ]

    project_ok = True

    for path in required_paths:
        if path.exists():
            print(f"[OK] {path.relative_to(ROOT)}")
        else:
            print(f"[MISSING] {path.relative_to(ROOT)}")
            project_ok = False

    ollama_ok = check_ollama()

    print("\nSummary")
    print(f"Project files: {'OK' if project_ok else 'CHECK REQUIRED'}")
    print(f"Ollama: {'OK' if ollama_ok else 'CHECK REQUIRED'}")

    return 0 if project_ok and ollama_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
