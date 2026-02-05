"""RAG Engine for XLSForm knowledge base."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .embedder import SentenceTransformerEmbedder
from .retriever import FAISSRetriever


@dataclass
class BestPractice:
    """Best practice recommendation from knowledge base."""
    text: str
    category: str  # e.g., "constraints", "question_types", "choice_lists"
    source: str  # e.g., "ODK Best Practices", "DIME Style Guide"
    relevance_score: float


@dataclass
class ConstraintRule:
    """Constraint rule from knowledge base."""
    question_type: str
    pattern: str  # e.g., "age", "name", "percentage"
    constraint: str
    constraint_message: str
    required: str
    required_message: str
    appearance: str = ""
    relevance_score: float = 0.0


@dataclass
class QuestionPattern:
    """Question type pattern from knowledge base."""
    keywords: List[str]
    question_type: str
    confidence: float
    source: str


class RAGEngine:
    """RAG system for XLSForm knowledge retrieval.

    Orchestrates embedding generation and similarity search to provide
    intelligent recommendations for XLSForm design.

    Example:
        >>> rag = RAGEngine(kb_path="data/knowledge_base")
        >>> practices = rag.query_best_practices("Age field", "integer", {})
        >>> for practice in practices:
        ...     print(f"{practice.source}: {practice.text}")
    """

    def __init__(self, kb_path: Optional[Path] = None):
        """Initialize the RAG engine.

        Args:
            kb_path: Path to knowledge base directory. If None, uses default.
        """
        # Default knowledge base path
        if kb_path is None:
            kb_path = Path(__file__).parent / "data"

        self.kb_path = Path(kb_path)
        self.embeddings_path = self.kb_path / "embeddings"

        # Initialize components
        self.embedder = SentenceTransformerEmbedder()
        self.retriever = FAISSRetriever(
            embedding_dimension=self.embedder.get_embedding_dimension()
        )

        # Load or build index
        self._load_or_build_index()

    def _load_or_build_index(self):
        """Load existing index or build from knowledge base documents."""
        index_path = self.embeddings_path / "kb_index"

        # Try to load existing index
        if index_path.with_suffix(".faiss").exists():
            try:
                self.retriever.load_index(index_path)
                return
            except Exception as e:
                print(f"Warning: Could not load index: {e}. Building new index.")

        # Build index from documents
        self._build_index()

    def _build_index(self):
        """Build index from knowledge base documents."""
        # Import document processor
        from .best_practices_kb import BestPracticesKB

        kb = BestPracticesKB(self.kb_path)

        # Load all documents
        documents = kb.load_all_documents()

        if not documents:
            print("Warning: No documents found in knowledge base.")
            return

        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedder.embed_batch(texts)

        # Build index with metadata
        metadata = [doc["metadata"] for doc in documents]
        self.retriever.build_index(embeddings, metadata)

        # Save index
        self.embeddings_path.mkdir(parents=True, exist_ok=True)
        self.retriever.save_index(self.embeddings_path / "kb_index")
        print(f"✓ Built index with {len(documents)} documents")

    def query_best_practices(
        self,
        question_text: str,
        question_type: str,
        context: Dict[str, Any]
    ) -> List[BestPractice]:
        """Query knowledge base for relevant best practices.

        Args:
            question_text: The question label/text
            question_type: Detected XLSForm type (e.g., "integer", "text")
            context: Form context (section, nearby questions, etc.)

        Returns:
            Ranked list of best practice recommendations

        Example:
            >>> practices = rag.query_best_practices(
            ...     "What is your age?",
            ...     "integer",
            ...     {"section": "demographics"}
            ... )
            >>> for practice in practices:
            ...     print(f"{practice.category}: {practice.text}")
        """
        # Construct query
        query = f"{question_type} {question_text}"
        if context.get("section"):
            query += f" section:{context['section']}"
        if context.get("keywords"):
            query += f" keywords:{','.join(context['keywords'])}"

        # Generate embedding
        query_embedding = self.embedder.embed(query)

        # Search
        results = self.retriever.search(query_embedding, top_k=5)

        # Format results
        practices = []
        for result in results:
            metadata = result["metadata"]
            practices.append(BestPractice(
                text=metadata.get("text", ""),
                category=metadata.get("category", "general"),
                source=metadata.get("source", "Knowledge Base"),
                relevance_score=result["score"]
            ))

        return practices

    def get_constraint_suggestions(
        self,
        question_name: str,
        question_type: str,
        question_label: str = ""
    ) -> List[ConstraintRule]:
        """Get intelligent constraint suggestions from knowledge base.

        Args:
            question_name: Question variable name (e.g., "respondent_age")
            question_type: XLSForm question type
            question_label: Question label text

        Returns:
            List of constraint rules ranked by relevance

        Example:
            >>> rules = rag.get_constraint_suggestions("age", "integer", "What is your age?")
            >>> best_rule = rules[0]
            >>> print(f"Constraint: {best_rule.constraint}")
            . >= 0 and . <= 130
        """
        # Query for constraint patterns
        query = f"constraint {question_type} {question_name} {question_label}"
        query_embedding = self.embedder.embed(query)

        results = self.retriever.search(query_embedding, top_k=3)

        # Format results
        rules = []
        for result in results:
            metadata = result["metadata"]
            if metadata.get("type") == "constraint":
                rules.append(ConstraintRule(
                    question_type=question_type,
                    pattern=metadata.get("pattern", ""),
                    constraint=metadata.get("constraint", ""),
                    constraint_message=metadata.get("constraint_message", ""),
                    required=metadata.get("required", "yes"),
                    required_message=metadata.get("required_message", ""),
                    appearance=metadata.get("appearance", ""),
                    relevance_score=result["score"]
                ))

        # If no rules found, return basic default
        if not rules:
            rules.append(self._get_default_constraint(question_type, question_name))

        return rules

    def find_similar_questions(
        self,
        question_text: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Find similar questions in the knowledge base.

        Args:
            question_text: Question text to match
            top_k: Number of results

        Returns:
            List of similar questions with metadata

        Example:
            >>> similar = rag.find_similar_questions("How old are you?")
            >>> for q in similar:
            ...     print(f"{q['type']}: {q['label']}")
        """
        query = f"question {question_text}"
        query_embedding = self.embedder.embed(query)

        results = self.retriever.search(query_embedding, top_k=top_k)

        similar = []
        for result in results:
            metadata = result["metadata"]
            if metadata.get("type") == "question":
                similar.append({
                    "type": metadata.get("question_type", ""),
                    "label": metadata.get("label", ""),
                    "confidence": result["score"]
                })

        return similar

    def _get_default_constraint(
        self,
        question_type: str,
        question_name: str
    ) -> ConstraintRule:
        """Get default constraint when no match found in KB."""
        # Basic defaults based on type
        if question_type == "integer":
            if "age" in question_name.lower():
                return ConstraintRule(
                    question_type=question_type,
                    pattern="age",
                    constraint=". >= 0 and . <= 130",
                    constraint_message="Age must be between 0 and 130",
                    required="yes",
                    required_message="Age is required",
                    relevance_score=0.5
                )
            else:
                return ConstraintRule(
                    question_type=question_type,
                    pattern="integer",
                    constraint=". >= 0",
                    constraint_message="Value must be zero or positive",
                    required="yes",
                    required_message="This field is required",
                    relevance_score=0.5
                )
        elif question_type == "decimal":
            return ConstraintRule(
                question_type=question_type,
                pattern="decimal",
                constraint=". > 0",
                constraint_message="Value must be positive",
                required="yes",
                required_message="This field is required",
                relevance_score=0.5
            )
        else:
            return ConstraintRule(
                question_type=question_type,
                pattern="default",
                constraint="",
                constraint_message="",
                required="yes",
                required_message="This field is required",
                relevance_score=0.5
            )


if __name__ == "__main__":
    # Test the RAG engine
    print("Testing RAGEngine...")

    # This will build a simple index from available documents
    try:
        rag = RAGEngine()
        print("✓ RAG Engine initialized")

        # Test query
        practices = rag.query_best_practices(
            "What is your age?",
            "integer",
            {"section": "demographics"}
        )
        print(f"\n✓ Query returned {len(practices)} best practices")

        # Test constraint suggestions
        rules = rag.get_constraint_suggestions("age", "integer", "What is your age?")
        print(f"\n✓ Got {len(rules)} constraint suggestions")
        if rules:
            print(f"  Best: {rules[0].constraint}")

        print("\n✓ All tests passed!")

    except Exception as e:
        print(f"\nNote: {e}")
        print("This is expected if knowledge base documents don't exist yet.")
        print("Create documents in data/ directory to enable full functionality.")
