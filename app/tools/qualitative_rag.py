
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import tool

from app.config import settings


def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.embedding_model
    )

    vector_dir = Path(settings.vector_dir)

    if not (vector_dir / "index.faiss").exists():
        raise FileNotFoundError(
            "FAISS index not found. Please build the vectorstore first."
        )

    store = FAISS.load_local(
        str(vector_dir),
        embeddings,
        allow_dangerous_deserialization=True
    )

    return store


@tool
def qualitative_analysis_tool(
    question: str,
    transcript_paths: list[str] | None = None
) -> dict:
    """Retrieve evidence from earnings call transcripts."""

    store = load_vectorstore()

    docs = store.similarity_search(question, k=6)

    return {
        "question": question,
        "evidence": [
            {
                "text": doc.page_content,
                "source": doc.metadata.get("source", "unknown")
            }
            for doc in docs
        ]
    }
