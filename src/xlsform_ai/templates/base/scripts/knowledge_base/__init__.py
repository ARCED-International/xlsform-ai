"""XLSForm AI Knowledge Base - RAG-powered best practices system."""

__all__ = ["RAGEngine", "SentenceTransformerEmbedder", "FAISSRetriever"]

try:
    from .rag_engine import RAGEngine
    from .embedder import SentenceTransformerEmbedder
    from .retriever import FAISSRetriever
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
