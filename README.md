# AI Interviewer — Local LLM-Powered Interview Platform

An AI-powered interview preparation platform built with Python and Streamlit. It helps candidates practice interviews, analyze resumes, retrieve information from uploaded documents, evaluate answers, and review their performance using locally hosted language models.

The project uses **Ollama** to run AI models locally, avoiding paid LLM API requirements.

## Features

- **User Authentication** — User registration and login.
- **AI Interview Practice** — Generate interview questions based on role, experience level, interview type, and difficulty.
- **Answer Evaluation** — Evaluate candidate answers and provide feedback.
- **Adaptive Interviews** — Support adaptive difficulty and follow-up recommendations.
- **Resume Analysis** — Extract information from PDF and DOCX resumes, identify skills, and compare them with job descriptions.
- **RAG Knowledge Base** — Upload documents, retrieve relevant content, and generate context-aware answers.
- **Dashboard** — Review interview history, scores, and performance metrics.
- **Reports** — Generate interview summaries and export reports.
- **Local AI Models** — Use Ollama for question generation, answer evaluation, and embeddings.
- **Voice Support** — Optional speech input/output, depending on installed dependencies and configured components.
- **SQLite Database** — Store application data locally.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.10 |
| User interface | Streamlit |
| LLM runtime | Ollama |
| Chat model | `qwen2.5:3b` |
| Embedding model | `nomic-embed-text` |
| Database | SQLite |
| Data validation | Pydantic |
| Document processing | PyPDF, python-docx |
| RAG and vector search | LangChain, ChromaDB |
| Testing | pytest |
| Version control | Git and GitHub |

## Project Structure

```text
AI_Interviewer/
├── app.py
├── config.py
├── database.py
├── logger_config.py
├── models.py
├── schemas.py
├── schemas_resume.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── services/
│   ├── auth_service.py
│   ├── question_generator.py
│   ├── answer_evaluator.py
│   ├── adaptive_interviewer.py
│   ├── interview_repository.py
│   ├── interview_settings.py
│   ├── interview_setup_ui.py
│   ├── interview_ui.py
│   ├── resume_parser.py
│   ├── resume_analyzer.py
│   ├── resume_ui.py
│   ├── rag_service.py
│   ├── knowledge_ui.py
│   ├── report_service.py
│   └── dashboard_service.py
└── tests/
```

*The exact files and subdirectories may differ depending on your current project version.*

## Prerequisites

Install the following before running the application:

- Python 3.10
- Git
- Ollama for Windows
- Sufficient RAM and disk space for the local AI models

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sandhya401/Ai_Interviewer.git
cd Ai_Interviewer
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, you can use Command Prompt instead:

```bat
venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Ollama

Download Ollama:

https://ollama.com/download/windows

Pull the chat model:

```bash
ollama pull qwen2.5:3b
```

Pull the embedding model:

```bash
ollama pull nomic-embed-text
```

Verify installed models:

```bash
ollama list
```

### 5. Configure environment variables

If `.env.example` exists, create your local `.env` file:

```powershell
Copy-Item .env.example .env
```

Review the variable names expected by `config.py` and the application services. Typical Ollama settings are:

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
DATABASE_URL=sqlite:///./ai_interviewer.db
```

Use the exact configuration keys required by your project. Do not commit your real `.env` file or any credentials to GitHub.

## Running the Application

Make sure Ollama is running and the required models are installed.

Start Streamlit:

```bash
streamlit run app.py
```

Open the local URL shown in the terminal. By default, it is:

http://localhost:8501

## How to Use

1. Register an account and log in.
2. Select the target job role and interview settings.
3. Generate interview questions.
4. Submit answers and review feedback.
5. Upload a resume to extract skills and analyze job-description alignment.
6. Upload supported knowledge documents to the RAG knowledge base.
7. Ask questions about the indexed documents.
8. Review interview history and dashboard metrics.
9. Export reports when the relevant report functionality is configured.
10. Explore optional voice features if their dependencies are installed.

Available features depend on the current implementation and configuration.

## Running Tests

If the project includes automated tests, install pytest if necessary:

```bash
pip install pytest
```

Run the test suite:

```bash
python -m pytest -q
```

Check Python syntax:

```bash
python -m compileall -q .
```

These checks do not replace testing the complete application and its Ollama integration.

## Privacy and Security

- Chat and embedding models are hosted locally through Ollama.
- Do not commit `.env` files, credentials, private resumes, interview records, or local databases.
- Review uploaded documents and generated reports before sharing them.
- Local execution does not automatically guarantee complete privacy; review application logging, storage, and network configuration.

## Troubleshooting

### Ollama connection error

Confirm that Ollama is running and check the installed models:

```bash
ollama list
```

### Missing Python module

Activate your virtual environment and install the appropriate dependency:

```bash
pip install -r requirements.txt
```

### Port 8501 is already in use

Run Streamlit on another port:

```bash
streamlit run app.py --server.port 8502
```

### PDF or DOCX parsing error

Verify that the document is supported, that it contains extractable text, and that the relevant dependencies are installed. Scanned PDFs may require OCR.

## Future Enhancements

- More detailed interview analytics.
- Improved adaptive question selection.
- Expanded resume-to-job matching.
- More robust RAG evaluation and source attribution.
- Additional speech recognition and text-to-speech options.
- Automated testing and deployment.
- Improved access controls and production security.

## Author

**Sandhya A.**

GitHub: https://github.com/sandhya401

## License

No license has been specified yet. Unless a license is added, standard copyright restrictions apply to reuse and redistribution.
