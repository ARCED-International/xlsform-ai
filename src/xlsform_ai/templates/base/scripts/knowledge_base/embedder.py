"""Sentence Transformer Embedder for XLSForm knowledge base."""

import numpy as np
from pathlib import Path
from typing import List, Union

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SentenceTransformerEmbedder:
    """Generate embeddings using sentence-transformers.

    Uses the lightweight all-MiniLM-L6-v2 model (384-dimensional embeddings,
    ~80MB model size) for fast inference and good semantic search quality.

    Example:
        >>> embedder = SentenceTransformerEmbedder()
        >>> embedding = embedder.embed("Age field should be between 0 and 130")
        >>> print(embedding.shape)  # (384,)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedder.

        Args:
            model_name: Name of the sentence-transformers model.
                       Default is all-MiniLM-L6-v2 (lightweight, fast).

        Raises:
            ImportError: If sentence-transformers is not installed.
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.model = None  # Lazy loading

    def _load_model(self):
        """Lazy load the model (only when first used)."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for a single text string.

        Args:
            text: Text to embed.

        Returns:
            Numpy array of shape (384,) for all-MiniLM-L6-v2.

        Example:
            >>> embedder = SentenceTransformerEmbedder()
            >>> embedding = embedder.embed("What is your age?")
            >>> print(embedding.shape)
            (384,)
        """
        self._load_model()
        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed.
            batch_size: Batch size for processing (default: 32).

        Returns:
            Numpy array of shape (len(texts), 384).

        Example:
            >>> embedder = SentenceTransformerEmbedder()
            >>> texts = ["Age question", "Name question", "Gender question"]
            >>> embeddings = embedder.embed_batch(texts)
            >>> print(embeddings.shape)
            (3, 384)
        """
        self._load_model()
        return self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)

    def save_embeddings(self, embeddings: np.ndarray, filepath: Union[str, Path]):
        """Save embeddings to disk for later reuse.

        Args:
            embeddings: Numpy array of embeddings.
            filepath: Path to save the embeddings (.pkl or .npy).

        Example:
            >>> embedder = SentenceTransformerEmbedder()
            >>> embeddings = embedder.embed_batch(["question 1", "question 2"])
            >>> embedder.save_embeddings(embeddings, "embeddings.pkl")
        """
        filepath = Path(filepath)

        if filepath.suffix == ".pkl":
            import pickle
            with open(filepath, "wb") as f:
                pickle.dump(embeddings, f)
        elif filepath.suffix == ".npy":
            np.save(filepath, embeddings)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}. Use .pkl or .npy")

    def load_embeddings(self, filepath: Union[str, Path]) -> np.ndarray:
        """Load embeddings from disk.

        Args:
            filepath: Path to the embeddings file (.pkl or .npy).

        Returns:
            Numpy array of embeddings.

        Example:
            >>> embedder = SentenceTransformerEmbedder()
            >>> embeddings = embedder.load_embeddings("embeddings.pkl")
            >>> print(embeddings.shape)
            (100, 384)
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Embeddings file not found: {filepath}")

        if filepath.suffix == ".pkl":
            import pickle
            with open(filepath, "rb") as f:
                return pickle.load(f)
        elif filepath.suffix == ".npy":
            return np.load(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}. Use .pkl or .npy")

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model.

        Returns:
            Embedding dimension (384 for all-MiniLM-L6-v2).

        Example:
            >>> embedder = SentenceTransformerEmbedder()
            >>> print(embedder.get_embedding_dimension())
            384
        """
        self._load_model()
        return self.model.get_sentence_embedding_dimension()


if __name__ == "__main__":
    # Test the embedder
    print("Testing SentenceTransformerEmbedder...")

    embedder = SentenceTransformerEmbedder()

    # Test single embedding
    text = "Age field should be between 0 and 130 years"
    embedding = embedder.embed(text)
    print(f"Single embedding shape: {embedding.shape}")
    print(f"First 5 values: {embedding[:5]}")

    # Test batch embedding
    texts = [
        "What is your age?",
        "Enter your name",
        "Select your gender",
        "How many children do you have?"
    ]
    embeddings = embedder.embed_batch(texts)
    print(f"\nBatch embeddings shape: {embeddings.shape}")

    # Test saving/loading
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        temp_path = f.name

    embedder.save_embeddings(embeddings, temp_path)
    print(f"\nSaved embeddings to: {temp_path}")

    loaded = embedder.load_embeddings(temp_path)
    print(f"Loaded embeddings shape: {loaded.shape}")
    print(f"Arrays equal: {np.array_equal(embeddings, loaded)}")

    # Clean up
    import os
    os.unlink(temp_path)

    print("\n[OK] All tests passed!")
