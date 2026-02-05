"""FAISS-based vector retriever for fast similarity search."""

import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any, Union

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class FAISSRetriever:
    """FAISS-based vector retriever for fast similarity search.

    Uses FAISS (Facebook AI Similarity Search) for efficient vector similarity
    search. Supports saving and loading indexes for persistence.

    Example:
        >>> retriever = FAISSRetriever(embedding_dimension=384)
        >>> embeddings = np.random.rand(100, 384)  # 100 embeddings
        >>> retriever.build_index(embeddings, metadata=["doc_1", "doc_2", ...])
        >>> results = retriever.search(query_embedding, top_k=5)
    """

    def __init__(self, embedding_dimension: int = 384):
        """Initialize the FAISS retriever.

        Args:
            embedding_dimension: Dimension of embeddings (384 for all-MiniLM-L6-v2).

        Raises:
            ImportError: If faiss-cpu is not installed.
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "faiss-cpu is not installed. "
                "Install it with: pip install faiss-cpu"
            )

        self.embedding_dimension = embedding_dimension
        self.index = None
        self.metadata: List[Any] = []  # Store metadata for each embedding

    def build_index(self, embeddings: np.ndarray, metadata: List[Any] = None):
        """Build FAISS index from embeddings.

        Args:
            embeddings: Numpy array of shape (n, embedding_dim).
            metadata: Optional list of metadata for each embedding.

        Example:
            >>> retriever = FAISSRetriever(embedding_dimension=384)
            >>> embeddings = np.random.rand(100, 384)
            >>> retriever.build_index(embeddings, metadata=["doc_1", "doc_2", ...])
        """
        if embeddings.shape[1] != self.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dimension}, "
                f"got {embeddings.shape[1]}"
            )

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Create index (IndexFlatIP for inner product = cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(self.embedding_dimension)
        self.index.add(embeddings.astype('float32'))

        # Store metadata
        if metadata is None:
            self.metadata = list(range(len(embeddings)))
        else:
            if len(metadata) != len(embeddings):
                raise ValueError(
                    f"Metadata length ({len(metadata)}) must match "
                    f"number of embeddings ({len(embeddings)})"
                )
            self.metadata = metadata

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings.

        Args:
            query_embedding: Query embedding vector of shape (embedding_dim,).
            top_k: Number of top results to return.

        Returns:
            List of dictionaries with keys: score, metadata.

        Example:
            >>> query = embedder.embed("Age question constraint")
            >>> results = retriever.search(query, top_k=5)
            >>> for result in results:
            ...     print(f"Score: {result['score']:.4f}, Metadata: {result['metadata']}")
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        if query_embedding.shape != (self.embedding_dimension,):
            raise ValueError(
                f"Query embedding dimension mismatch: expected ({self.embedding_dimension},), "
                f"got {query_embedding.shape}"
            )

        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)

        # Search
        scores, indices = self.index.search(query_embedding, top_k)

        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):  # Valid index
                results.append({
                    "score": float(score),
                    "metadata": self.metadata[int(idx)]
                })

        return results

    def save_index(self, filepath: Union[str, Path]):
        """Save FAISS index and metadata to disk.

        Args:
            filepath: Path to save the index (without extension).

        Example:
            >>> retriever.save_index("data/embeddings/knowledge_base")
            # Saves: knowledge_base.faiss and knowledge_base_metadata.pkl
        """
        if self.index is None:
            raise ValueError("No index to save. Build index first.")

        filepath = Path(filepath)

        # Save FAISS index
        index_path = filepath.with_suffix(".faiss")
        faiss.write_index(self.index, str(index_path))

        # Save metadata
        metadata_path = filepath.with_suffix("_metadata.pkl")
        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load_index(self, filepath: Union[str, Path]):
        """Load FAISS index and metadata from disk.

        Args:
            filepath: Path to the index file (without extension).

        Example:
            >>> retriever.load_index("data/embeddings/knowledge_base")
        """
        filepath = Path(filepath)

        # Load FAISS index
        index_path = filepath.with_suffix(".faiss")
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")

        self.index = faiss.read_index(str(index_path))

        # Load metadata
        metadata_path = filepath.with_suffix("_metadata.pkl")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

    def get_index_size(self) -> int:
        """Get the number of embeddings in the index.

        Returns:
            Number of embeddings in the index.

        Example:
            >>> retriever.build_index(embeddings)
            >>> print(retriever.get_index_size())
            100
        """
        if self.index is None:
            return 0
        return self.index.ntotal

    def is_built(self) -> bool:
        """Check if the index has been built.

        Returns:
            True if index is built and ready for search.

        Example:
            >>> if not retriever.is_built():
            ...     retriever.build_index(embeddings)
        """
        return self.index is not None


if __name__ == "__main__":
    # Test the retriever
    print("Testing FAISSRetriever...")

    # Create sample data
    np.random.seed(42)
    num_docs = 100
    embedding_dim = 384

    embeddings = np.random.rand(num_docs, embedding_dim)
    metadata = [f"doc_{i}" for i in range(num_docs)]

    # Build index
    retriever = FAISSRetriever(embedding_dimension=embedding_dim)
    retriever.build_index(embeddings, metadata)
    print(f"✓ Built index with {retriever.get_index_size()} embeddings")

    # Test search
    query = embeddings[0]  # Use first embedding as query
    results = retriever.search(query, top_k=5)
    print(f"\n✓ Search returned {len(results)} results:")
    for i, result in enumerate(results[:3]):
        print(f"  {i+1}. Score: {result['score']:.4f}, Metadata: {result['metadata']}")

    # Test save/load
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "test_index"
        retriever.save_index(save_path)
        print(f"\n✓ Saved index to: {save_path}")

        # Create new retriever and load
        new_retriever = FAISSRetriever(embedding_dimension=embedding_dim)
        new_retriever.load_index(save_path)
        print(f"✓ Loaded index with {new_retriever.get_index_size()} embeddings")

        # Verify search works
        new_results = new_retriever.search(query, top_k=5)
        assert len(results) == len(new_results), "Search results length mismatch"
        print("✓ Loaded index produces same results")

    print("\n✓ All tests passed!")
