"""Best Practices Knowledge Base for XLSForm."""

from pathlib import Path
from typing import List, Dict, Any
import re


class BestPracticesKB:
    """Load and manage XLSForm best practices knowledge base.

    Reads markdown documents from the data/ directory and prepares them
    for embedding and retrieval.

    Example:
        >>> kb = BestPracticesKB("data/knowledge_base")
        >>> documents = kb.load_all_documents()
        >>> print(f"Loaded {len(documents)} documents")
    """

    def __init__(self, kb_path: Path):
        """Initialize the knowledge base.

        Args:
            kb_path: Path to knowledge base directory.
        """
        self.kb_path = Path(kb_path)

    def load_all_documents(self) -> List[Dict[str, Any]]:
        """Load all documents from the knowledge base.

        Returns:
            List of document dictionaries with keys: text, metadata

        Example:
            >>> kb = BestPracticesKB("data")
            >>> docs = kb.load_all_documents()
            >>> for doc in docs:
            ...     print(f"{doc['metadata']['source']}: {doc['text'][:50]}...")
        """
        documents = []

        # Load ODK best practices
        odk_path = self.kb_path / "odk_best_practices.md"
        if odk_path.exists():
            documents.extend(self._parse_markdown_document(
                odk_path,
                "ODK Best Practices",
                "best_practices"
            ))

        # Load DIME style guide
        dime_path = self.kb_path / "dime_style_guide.md"
        if dime_path.exists():
            documents.extend(self._parse_markdown_document(
                dime_path,
                "DIME Analytics Style Guide",
                "style_guide"
            ))

        # Load question type patterns
        patterns_path = self.kb_path / "question_type_patterns.md"
        if patterns_path.exists():
            documents.extend(self._parse_markdown_document(
                patterns_path,
                "Question Type Patterns",
                "patterns"
            ))

        # Load constraint rules
        constraints_path = self.kb_path / "constraint_rules.md"
        if constraints_path.exists():
            documents.extend(self._parse_constraint_rules(
                constraints_path,
                "Constraint Rules"
            ))

        return documents

    def _parse_markdown_document(
        self,
        filepath: Path,
        source: str,
        category: str
    ) -> List[Dict[str, Any]]:
        """Parse a markdown document into chunks.

        Args:
            filepath: Path to markdown file
            source: Document source name
            category: Document category

        Returns:
            List of document chunks
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into sections based on headers
        sections = self._split_into_sections(content)

        # Create documents from sections
        documents = []
        for section in sections:
            if len(section.strip()) < 50:  # Skip very short sections
                continue

            documents.append({
                "text": section.strip(),
                "metadata": {
                    "source": source,
                    "category": category,
                    "type": "general"
                }
            })

        return documents

    def _split_into_sections(self, content: str) -> List[str]:
        """Split markdown content into sections based on headers.

        Args:
            content: Markdown content

        Returns:
            List of section texts
        """
        # Split by headers (## or ###)
        sections = re.split(r'\n#{2,3}\s+', content)

        # Filter out empty sections and the title
        sections = [s.strip() for s in sections if s.strip()]

        return sections

    def _parse_constraint_rules(
        self,
        filepath: Path,
        source: str
    ) -> List[Dict[str, Any]]:
        """Parse constraint rules markdown file.

        Args:
            filepath: Path to constraint rules file
            source: Document source

        Returns:
            List of constraint rule documents
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        documents = []

        # Parse constraint rules
        # Expected format:
        ## Pattern: age
        ### Type: integer
        ### Constraint: . >= 0 and . <= 130
        ### Message: Age must be between 0 and 130
        # (and any description)

        pattern_blocks = re.split(r'##\s+', content)

        for block in pattern_blocks[1:]:  # Skip first empty block
            lines = block.strip().split('\n')
            if len(lines) < 4:
                continue

            # Parse pattern name
            pattern_match = re.match(r'Pattern:\s*(.+)', lines[0])
            if not pattern_match:
                continue
            pattern = pattern_match.group(1).strip()

            # Parse other fields
            rule = {
                "pattern": pattern,
                "type": "constraint"
            }

            for line in lines[1:]:
                if line.startswith("### Type:"):
                    rule["question_type"] = line.split(":", 1)[1].strip()
                elif line.startswith("### Constraint:"):
                    rule["constraint"] = line.split(":", 1)[1].strip()
                elif line.startswith("### Message:"):
                    rule["constraint_message"] = line.split(":", 1)[1].strip()
                elif line.startswith("### Required:"):
                    rule["required"] = line.split(":", 1)[1].strip()
                elif line.startswith("### Required Message:"):
                    rule["required_message"] = line.split(":", 1)[1].strip()
                elif line.startswith("### Appearance:"):
                    rule["appearance"] = line.split(":", 1)[1].strip()

            # Create document
            text = f"Constraint for {pattern} ({rule.get('question_type', 'unknown')}): {rule.get('constraint', '')}"
            description = '\n'.join(lines[6:])  # Any remaining text is description
            if description:
                text += f" {description}"

            documents.append({
                "text": text,
                "metadata": {
                    **rule,
                    "source": source,
                    "category": "constraints"
                }
            })

        return documents


if __name__ == "__main__":
    # Test the knowledge base loader
    print("Testing BestPracticesKB...")

    kb = BestPracticesKB(Path(__file__).parent / "data")

    documents = kb.load_all_documents()

    print(f"[OK] Loaded {len(documents)} documents")

    # Show sample documents
    for i, doc in enumerate(documents[:3]):
        print(f"\nDocument {i+1}:")
        print(f"  Source: {doc['metadata']['source']}")
        print(f"  Category: {doc['metadata']['category']}")
        print(f"  Text: {doc['text'][:100]}...")

    print("\n[OK] Test complete!")
