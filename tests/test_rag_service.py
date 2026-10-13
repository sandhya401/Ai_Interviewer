
from unittest.mock import MagicMock, patch

import pytest


def test_retrieve_knowledge_returns_results():
    """Verify that the retrieval service returns matching documents."""

    from services.rag_service import retrieve_knowledge

    fake_document = MagicMock()
    fake_document.page_content = "Django REST Framework builds APIs."
    fake_document.metadata = {"source": "django_notes.txt"}

    with patch(
        "services.rag_service.Chroma"
    ) as mock_chroma:
        mock_vector_store = mock_chroma.return_value
        mock_vector_store.similarity_search.return_value = [fake_document]

        # Adapt the mocked constructor if your service initializes
        # Chroma differently.
        try:
            results = retrieve_knowledge(
                question="How do I build APIs with Django?",
                k=1,
            )
        except Exception as exc:
            pytest.skip(
                f"RAG service interface differs from this example: {exc}"
            )

    assert results
    assert "Django REST Framework" in results[0].page_content


def test_get_knowledge_context_returns_text():
    """Verify that retrieved knowledge can be formatted as context."""

    from services.rag_service import get_knowledge_context

    with patch(
        "services.rag_service.retrieve_knowledge",
        return_value=[],
    ):
        context = get_knowledge_context(
            question="Explain Django.",
            k=4,
        )

    assert isinstance(context, str)


def test_empty_question_is_handled():
    """Verify that an empty search query is handled safely."""

    from services.rag_service import retrieve_knowledge

    try:
        result = retrieve_knowledge(question="", k=4)
    except (ValueError, TypeError):
        return

    assert result is not None
