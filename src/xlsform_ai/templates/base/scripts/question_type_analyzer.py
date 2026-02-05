"""Question Type Analyzer - Intelligent question type detection with numeric preference.

This module provides smart question type detection following the principle:
- Primary: Use numeric choices (select_one/select_multiple) with numeric codes
- Secondary: Use integer or decimal if no discrete options
- Fallback: Use text only if clearly text-only (names, addresses, descriptions)
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class QuestionTypeDecision:
    """Decision about question type with confidence and reasoning."""
    type: str  # XLSForm question type (e.g., "integer", "select_one gender")
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Explanation for the decision
    numeric_codes: Optional[List[Dict[str, str]]] = None  # For select questions
    list_name: Optional[str] = None  # For select questions


class QuestionTypeAnalyzer:
    """Smart question type detection with aggressive numeric preference.

    Follows the decision strategy:
    1. If options provided → select_one/select_multiple (with numeric codes)
    2. If numeric keywords detected → integer/decimal (aggressive)
    3. Query RAG for similar questions (if available)
    4. Fallback to text only if clearly text-only

    Example:
        >>> analyzer = QuestionTypeAnalyzer()
        >>> decision = analyzer.detect_type("What is your age?")
        >>> print(decision.type)  # "integer"
        >>> print(decision.confidence)  # 0.85
    """

    # Keywords indicating integer type
    INTEGER_KEYWORDS = [
        'age', 'how old', 'years old',
        'count', 'number', 'how many',
        'frequency', 'how often',
        'years', 'months', 'weeks', 'days',
        'children', 'members', 'people',
        'times', 'occurrences',
        'quantity', 'amount'
    ]

    # Keywords indicating decimal type
    DECIMAL_KEYWORDS = [
        'weight', 'height', 'length',
        'price', 'cost', 'income', 'salary', 'wage',
        'percentage', 'percent', 'rate',
        'temperature',
        'distance', 'area',
        'size'
    ]

    # Keywords indicating text-only type
    TEXT_ONLY_PATTERNS = [
        r'\bname\b',  # name, first name, last name
        r'\baddress\b',
        r'\bdescribe\b',
        r'\bexplain\b',
        r'\bspecify\b',
        r'\bcomment\b',
        r'\bopen.?ended\b',
        r'\bwhat is your (?!age|weight|height|income)'  # Negative lookahead for measurements
    ]

    # Keywords indicating select_one
    SELECT_ONE_KEYWORDS = [
        'which one', 'choose one', 'select one',
        'what is your', 'what type of', 'what kind of'
    ]

    # Keywords indicating select_multiple
    SELECT_MULTIPLE_KEYWORDS = [
        'select all', 'check all', 'check all that apply',
        'choose all', 'select multiple', 'multiple choice',
        'which of these', 'what are all'
    ]

    def __init__(self, rag_engine=None):
        """Initialize the analyzer.

        Args:
            rag_engine: Optional RAGEngine for similarity matching.
        """
        self.rag_engine = rag_engine

    def detect_type(
        self,
        question_text: str,
        options: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> QuestionTypeDecision:
        """Detect XLSForm type with confidence score.

        Args:
            question_text: The question label
            options: List of choice options (if any)
            context: Form context (section, nearby questions, etc.)

        Returns:
            QuestionTypeDecision with type, confidence, reasoning

        Example:
            >>> analyzer = QuestionTypeAnalyzer()
            >>> decision = analyzer.detect_type("What is your age?")
            >>> print(f"{decision.type} (confidence: {decision.confidence})")
            integer (confidence: 0.85)
        """
        context = context or {}

        # Priority 1: Check for choice options
        if options:
            return self._detect_select_type(question_text, options)

        # Priority 2: Aggressive numeric detection
        numeric_decision = self._detect_numeric_type(question_text, context)
        if numeric_decision.confidence > 0.7:
            return numeric_decision

        # Priority 3: RAG-based similarity (if available)
        if self.rag_engine:
            try:
                rag_suggestion = self._query_rag_similarity(question_text)
                if rag_suggestion and rag_suggestion.confidence > 0.8:
                    return rag_suggestion
            except Exception as e:
                # RAG failed, continue to other methods
                pass

        # Priority 4: Text-only keywords check
        if self._is_text_only_question(question_text):
            return QuestionTypeDecision(
                type="text",
                confidence=0.85,
                reasoning="Text-only keywords detected (name, address, description, etc.)"
            )

        # Priority 5: Check for yes/no pattern
        if self._is_yes_no_question(question_text):
            return QuestionTypeDecision(
                type="select_one yes_no",
                confidence=0.9,
                reasoning="Yes/No question pattern detected"
            )

        # Default to text (conservative fallback)
        return QuestionTypeDecision(
            type="text",
            confidence=0.3,
            reasoning="No strong indicator detected, defaulting to text"
        )

    def _detect_select_type(
        self,
        question_text: str,
        options: List[str]
    ) -> QuestionTypeDecision:
        """Detect select_one vs select_multiple with numeric coding.

        Args:
            question_text: The question text
            options: List of choice options

        Returns:
            QuestionTypeDecision for select type
        """
        # Check for select_multiple indicators
        question_lower = question_text.lower()
        is_multiple = any(
            keyword in question_lower
            for keyword in self.SELECT_MULTIPLE_KEYWORDS
        )

        # Generate numeric codes for options
        numeric_options = [
            {"name": str(i + 1), "label": opt.strip()}
            for i, opt in enumerate(options)
        ]

        # Generate list name from question text
        list_name = self._generate_list_name(question_text)

        # Determine select type
        select_type = "select_multiple" if is_multiple else "select_one"
        full_type = f"{select_type} {list_name}"

        reasoning = f"Choice options provided ({len(options)} options) - using numeric codes 1-{len(options)}"

        return QuestionTypeDecision(
            type=full_type,
            confidence=0.95,
            reasoning=reasoning,
            numeric_codes=numeric_options,
            list_name=list_name
        )

    def _detect_numeric_type(
        self,
        question_text: str,
        context: Dict[str, Any]
    ) -> QuestionTypeDecision:
        """Detect integer or decimal type with aggressive numeric preference.

        Args:
            question_text: The question text
            context: Form context

        Returns:
            QuestionTypeDecision for numeric type
        """
        question_lower = question_text.lower()

        # Check for decimal indicators (higher priority)
        decimal_match = None
        for keyword in self.DECIMAL_KEYWORDS:
            if keyword in question_lower:
                decimal_match = keyword
                break

        if decimal_match:
            # Special case for percentage
            if 'percent' in question_lower:
                return QuestionTypeDecision(
                    type="decimal",
                    confidence=0.9,
                    reasoning=f"Percentage keyword detected: '{decimal_match}'"
                )
            else:
                return QuestionTypeDecision(
                    type="decimal",
                    confidence=0.85,
                    reasoning=f"Decimal keyword detected: '{decimal_match}'"
                )

        # Check for integer indicators
        integer_match = None
        for keyword in self.INTEGER_KEYWORDS:
            if keyword in question_lower:
                integer_match = keyword
                break

        if integer_match:
            return QuestionTypeDecision(
                type="integer",
                confidence=0.85,
                reasoning=f"Integer keyword detected: '{integer_match}'"
            )

        # No numeric keywords found
        return QuestionTypeDecision(
            type="",
            confidence=0.0,
            reasoning="No numeric keywords detected"
        )

    def _is_text_only_question(self, question_text: str) -> bool:
        """Check if question MUST be text (names, addresses, etc.).

        Args:
            question_text: The question text

        Returns:
            True if clearly text-only
        """
        question_lower = question_text.lower()

        # Check against text-only patterns
        for pattern in self.TEXT_ONLY_PATTERNS:
            if re.search(pattern, question_lower):
                return True

        return False

    def _is_yes_no_question(self, question_text: str) -> bool:
        """Check if this is a yes/no question.

        Args:
            question_text: The question text

        Returns:
            True if yes/no pattern detected
        """
        question_lower = question_text.lower()

        # Common yes/no patterns
        yes_no_patterns = [
            r'\bdo you\b',
            r'\bdid you\b',
            r'\bhave you\b',
            r'\bwill you\b',
            r'\bcan you\b',
            r'\bis it\b',
            r'\bare you\b',
            r'\byes or no\b'
        ]

        return any(re.search(pattern, question_lower) for pattern in yes_no_patterns)

    def _generate_list_name(self, question_text: str) -> str:
        """Generate a choice list name from question text.

        Args:
            question_text: The question text

        Returns:
            Generated list name (snake_case)
        """
        # Remove common question words
        question_words_to_remove = [
            'what', 'which', 'select', 'choose', 'your',
            'is', 'are', 'the', 'a', 'an'
        ]

        # Extract key words
        words = question_text.lower().split()
        key_words = [
            w for w in words
            if w not in question_words_to_remove
            and len(w) > 2
            and w.isalpha()
        ]

        # Take first 2-3 key words
        list_name = '_'.join(key_words[:3])

        # Ensure it's not empty
        if not list_name:
            list_name = "choices"

        return list_name

    def _query_rag_similarity(
        self,
        question_text: str
    ) -> Optional[QuestionTypeDecision]:
        """Query RAG engine for similar questions.

        Args:
            question_text: The question text

        Returns:
            QuestionTypeDecision based on RAG results, or None
        """
        if not self.rag_engine:
            return None

        try:
            similar = self.rag_engine.find_similar_questions(question_text, top_k=1)

            if similar and similar[0].get('confidence', 0) > 0.8:
                return QuestionTypeDecision(
                    type=similar[0]['type'],
                    confidence=similar[0]['confidence'],
                    reasoning=f"Similar question found in knowledge base: {similar[0]['label'][:50]}..."
                )
        except Exception:
            pass

        return None


if __name__ == "__main__":
    # Test the analyzer
    print("Testing QuestionTypeAnalyzer...\n")

    analyzer = QuestionTypeAnalyzer()

    test_cases = [
        ("What is your age?", None),
        ("Enter your weight in kg", None),
        ("What is your name?", None),
        ("Describe your main activity", None),
        ("Do you own a phone?", None),
        ("Select all sources of income", ["Wage", "Business", "Rental"]),
        ("How many children do you have?", None),
        ("What percentage of your income?", None),
        ("Select your gender", ["Male", "Female", "Other"]),
        ("Check all that apply", ["Option 1", "Option 2", "Option 3"]),
    ]

    for question, options in test_cases:
        decision = analyzer.detect_type(question, options)
        print(f"Question: {question}")
        print(f"  Type: {decision.type}")
        print(f"  Confidence: {decision.confidence:.2f}")
        print(f"  Reasoning: {decision.reasoning}")
        if decision.numeric_codes:
            print(f"  Numeric Codes: {len(decision.numeric_codes)} options")
        print()

    print("[OK] All tests completed!")
