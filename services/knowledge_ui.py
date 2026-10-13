
import os
import tempfile
from pathlib import Path

import streamlit as st

from services.rag_service import (
    answer_from_knowledge,
    ingest_file,
    retrieve_knowledge,
)


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def render_knowledge_ui():
    """Render the local RAG knowledge-base screen."""

    st.title("Knowledge Base — RAG")
    st.caption(
        "Upload documents and ask questions using your local AI model."
    )

    st.subheader("1. Add a document")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["txt", "md", "pdf"],
        key="knowledge_upload",
        help="Supported formats: TXT, Markdown, and PDF. Maximum 10 MB.",
    )

    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix.lower()

        if suffix not in SUPPORTED_EXTENSIONS:
            st.error("This document format is not supported.")

        elif len(uploaded_file.getvalue()) > MAX_FILE_SIZE:
            st.error("The document must be 10 MB or smaller.")

        elif st.button(
            "Add to Knowledge Base",
            type="primary",
            key="ingest_knowledge_document",
        ):
            temporary_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=suffix,
                    delete=False,
                ) as temporary_file:
                    temporary_file.write(uploaded_file.getvalue())
                    temporary_path = temporary_file.name

                with st.spinner(
                    "Processing document and creating embeddings..."
                ):
                    result = ingest_file(
                        temporary_path,
                        source_name=uploaded_file.name,
                    )

                st.success("Document ingestion completed.")
                if result is not None:
                    st.write(result)

            except Exception as exc:
                st.error(
                    "Document ingestion failed. Check the embedding "
                    "model and ChromaDB configuration."
                )
                print(f"Knowledge ingestion error: {exc}")

            finally:
                if temporary_path and os.path.exists(temporary_path):
                    try:
                        os.remove(temporary_path)
                    except OSError:
                        pass

    st.divider()
    st.subheader("2. Ask a question")

    question = st.text_area(
        "What would you like to know?",
        placeholder=(
            "Example: Explain the main concepts in my uploaded document."
        ),
        height=100,
        key="knowledge_question",
    )

    if st.button(
        "Search Knowledge Base",
        type="primary",
        key="search_knowledge_base",
        disabled=not question.strip(),
    ):
        try:
            with st.spinner("Searching relevant document sections..."):
                # Retrieve matching document chunks.
                retrieved = retrieve_knowledge(
                    question=question,
                    k=4,
                )

                st.session_state.knowledge_results = retrieved
                st.session_state.knowledge_question_result = question
                answer_result = answer_from_knowledge(
                    question=question,
                    k=4,
                    context_results=retrieved,
                )
                st.session_state.knowledge_context = answer_result["context"]
                st.session_state.knowledge_answer = answer_result["answer"]

        except Exception as exc:
            st.error(
                "Knowledge retrieval failed. Make sure the knowledge "
                "base has documents and the local models are available. "
                f"Details: {exc}"
            )
            print(f"Knowledge retrieval error: {exc}")

    retrieved = st.session_state.get("knowledge_results")
    context = st.session_state.get("knowledge_context")
    answer = st.session_state.get("knowledge_answer")

    if retrieved is not None:
        st.markdown("### Answer")
        if answer:
            st.write(answer)

        st.markdown("### Retrieved document sections")

        if not retrieved:
            st.info(
                "No relevant sections were found. Add documents or try "
                "a different question."
            )
        else:
            for index, item in enumerate(retrieved, start=1):
                # Support either LangChain Document objects or dictionaries.
                if isinstance(item, dict):
                    content = item.get("page_content", item.get("content", ""))
                    metadata = item.get("metadata", {})
                else:
                    content = getattr(item, "page_content", str(item))
                    metadata = getattr(item, "metadata", {})

                source = metadata.get("source", "Unknown source")
                page = metadata.get("page")

                label = f"Result {index} — {Path(str(source)).name}"
                if page is not None:
                    label += f" — Page {page}"

                with st.expander(label):
                    st.write(content)

        if context:
            with st.expander("View combined retrieved context"):
                st.text(context)

    st.caption(
        "Answers are generated from the indexed document sections using your local AI model."
    )
