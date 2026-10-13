
from services.rag_service import ingest_directory


if __name__ == "__main__":
    result = ingest_directory()

    print(f"Knowledge directory: {result['directory']}")
    print(f"Total chunks processed: {result['total_chunks']}")

    for file_path, details in result["files"].items():
        print(
            f"{details['status'].upper()}: {file_path} "
            f"({details['chunks']} chunks)"
        )

        if details.get("message"):
            print(f"  Error: {details['message']}")
