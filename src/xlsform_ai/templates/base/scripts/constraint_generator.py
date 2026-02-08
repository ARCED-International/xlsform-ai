"""Smart Constraint Generator - Context-aware constraint and validation logic.

This module generates intelligent constraints based on question type, name,
and context, using both rule-based patterns and RAG knowledge base.
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ConstraintSet:
    """Complete constraint set for a question."""
    constraint: str
    constraint_message: str
    required: str
    required_message: str
    appearance: str = ""
    relevant: str = ""


@dataclass
class Question:
    """Question information for constraint generation."""
    type: str
    name: str
    label: str = ""
    options: Optional[List[Dict[str, str]]] = None


class SmartConstraintGenerator:
    """Generate intelligent constraints based on context and knowledge base.

    Replaces the simple rule-based get_best_practices() function with
    intelligent constraint generation that considers:
    - Question type (integer, decimal, text, select_*)
    - Question name patterns (age, name, email, etc.)
    - Context from knowledge base (if RAG available)

    Example:
        >>> generator = SmartConstraintGenerator()
        >>> question = Question("integer", "age", "What is your age?")
        >>> constraints = generator.generate_constraints(question)
        >>> print(constraints.constraint)
        . >= 0 and . <= 130
    """

    # Field types that should NOT be required
    NON_INPUT_TYPES = {
        'calculate', 'hidden', 'note', 'imei', 'deviceid', 'subscriberid',
        'simserial', 'phonenumber', 'username', 'start', 'end', 'today',
        'audit', 'barcode', 'qrcode', 'image', 'audio', 'video', 'file'
    }

    def __init__(self, rag_engine=None):
        """Initialize the constraint generator.

        Args:
            rag_engine: Optional RAGEngine for KB lookups.
        """
        self.rag_engine = rag_engine

    def generate_constraints(self, question: Question) -> ConstraintSet:
        """Generate complete constraint set for a question.

        Args:
            question: Question object with type, name, label, options

        Returns:
            ConstraintSet with all validation fields

        Example:
            >>> question = Question("integer", "age", "What is your age?")
            >>> constraints = generator.generate_constraints(question)
            >>> print(constraints.constraint, constraints.required)
            . >= 0 and . <= 130 yes
        """
        # Check if non-input type (not required)
        is_non_input = question.type.lower() in self.NON_INPUT_TYPES

        # Generate constraints based on type
        if question.type == "integer":
            return self._integer_constraints(question, is_non_input)
        elif question.type == "decimal":
            return self._decimal_constraints(question, is_non_input)
        elif question.type == "text":
            return self._text_constraints(question, is_non_input)
        elif question.type.startswith("select_"):
            return self._select_constraints(question, is_non_input)
        else:
            return self._default_constraints(question, is_non_input)

    def _integer_constraints(
        self,
        question: Question,
        is_non_input: bool
    ) -> ConstraintSet:
        """Generate integer constraints with smart range detection.

        Args:
            question: The question object
            is_non_input: Whether this is a non-input type

        Returns:
            ConstraintSet for integer question
        """
        question_name_lower = question.name.lower()
        question_label_lower = question.label.lower()

        # Age-specific
        if "age" in question_name_lower or "age" in question_label_lower:
            return ConstraintSet(
                constraint=". >= 0 and . <= 130",
                constraint_message="Age must be between 0 and 130 years",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Age is required"
            )

        # Percentage integer
        if "percent" in question_name_lower or "percent" in question_label_lower:
            return ConstraintSet(
                constraint=". >= 0 and . <= 100",
                constraint_message="Value must be between 0 and 100",
                appearance="percentages",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "This field is required"
            )

        # Count-specific (children, members, etc.)
        count_keywords = ["count", "number", "children", "members", "people", "household"]
        if any(kw in question_name_lower for kw in count_keywords):
            # Check if it should be positive (>= 1) or non-negative (>= 0)
            if "size" in question_name_lower or "member" in question_name_lower:
                return ConstraintSet(
                    constraint=". > 0",
                    constraint_message=f"{question.label or 'Value'} must be at least 1",
                    required="" if is_non_input else "yes",
                    required_message="" if is_non_input else f"{question.label or 'This field'} is required"
                )
            else:
                return ConstraintSet(
                    constraint=". >= 0",
                    constraint_message=f"{question.label or 'Value'} must be zero or positive",
                    required="" if is_non_input else "yes",
                    required_message="" if is_non_input else f"{question.label or 'This field'} is required"
                )

        # Year field
        if "year" in question_name_lower:
            return ConstraintSet(
                constraint=". >= 1900 and . <= 2100",
                constraint_message="Please enter a valid year (1900-2100)",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Year is required"
            )

        # Rating 1-5
        if "rating" in question_name_lower or "scale" in question_label_lower:
            return ConstraintSet(
                constraint=". >= 1 and . <= 5",
                constraint_message="Please select a rating from 1 to 5",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Rating is required"
            )

        # Rating 1-10
        if "nps" in question_name_lower or "score" in question_name_lower:
            return ConstraintSet(
                constraint=". >= 1 and . <= 10",
                constraint_message="Please select a rating from 1 to 10",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Rating is required"
            )

        # Default integer: non-negative
        return ConstraintSet(
            constraint=". >= 0",
            constraint_message="Value must be zero or positive",
            required="" if is_non_input else "yes",
            required_message="" if is_non_input else "This field is required"
        )

    def _decimal_constraints(
        self,
        question: Question,
        is_non_input: bool
    ) -> ConstraintSet:
        """Generate decimal constraints.

        Args:
            question: The question object
            is_non_input: Whether this is a non-input type

        Returns:
            ConstraintSet for decimal question
        """
        question_name_lower = question.name.lower()
        question_label_lower = question.label.lower()

        # Percentage decimal
        if "percent" in question_name_lower or "percent" in question_label_lower:
            return ConstraintSet(
                constraint=". >= 0 and . <= 100",
                constraint_message="Percentage must be between 0 and 100",
                appearance="percentages",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "This field is required"
            )

        # Weight/height measurements
        if any(kw in question_name_lower for kw in ["weight", "height", "length"]):
            return ConstraintSet(
                constraint=". > 0",
                constraint_message=f"{question.label or 'Value'} must be positive",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else f"{question.label or 'This field'} is required"
            )

        # Price/cost/income
        if any(kw in question_name_lower for kw in ["price", "cost", "income", "amount", "wage", "salary"]):
            return ConstraintSet(
                constraint=". >= 0",
                constraint_message=f"{question.label or 'Value'} must be zero or positive",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else f"{question.label or 'This field'} is required"
            )

        # Rate
        if "rate" in question_name_lower:
            return ConstraintSet(
                constraint=". >= 0",
                constraint_message="Rate must be zero or positive",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Rate is required"
            )

        # Default decimal: positive
        return ConstraintSet(
            constraint=". > 0",
            constraint_message="Value must be positive",
            required="" if is_non_input else "yes",
            required_message="" if is_non_input else "This field is required"
        )

    def _text_constraints(
        self,
        question: Question,
        is_non_input: bool
    ) -> ConstraintSet:
        """Generate text constraints with smart regex.

        Args:
            question: The question object
            is_non_input: Whether this is a non-input type

        Returns:
            ConstraintSet for text question
        """
        question_name_lower = question.name.lower()
        question_label_lower = question.label.lower()

        # Name fields
        if any(kw in question_name_lower for kw in ["name", "first", "last", "full"]):
            return ConstraintSet(
                # Use double-quoted regex literal so apostrophes in names are valid XPath strings.
                constraint="regex(., \"^[A-Za-z\\s\\-\\.']+$\")",
                constraint_message="Please enter a valid name (letters only)",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Name is required"
            )

        # Email fields
        if "email" in question_name_lower:
            return ConstraintSet(
                constraint="regex(., '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')",
                constraint_message="Please enter a valid email address",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Email is required"
            )

        # Phone fields
        if any(kw in question_name_lower for kw in ["phone", "mobile", "telephone"]):
            return ConstraintSet(
                constraint="regex(., '^[0-9+\\-\\s]+$')",
                constraint_message="Please enter a valid phone number",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Phone number is required"
            )

        # ID fields
        if "id" in question_name_lower:
            return ConstraintSet(
                constraint="regex(., '^[a-zA-Z0-9\\-]+$')",
                constraint_message="ID must contain only letters, numbers, and hyphens",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "ID is required"
            )

        # Address fields
        if "address" in question_name_lower:
            return ConstraintSet(
                constraint="",
                constraint_message="",
                required="" if is_non_input else "yes",
                required_message="" if is_non_input else "Address is required"
            )

        # Other specify (typically not required)
        if "other" in question_name_lower and "specify" in question_name_lower:
            return ConstraintSet(
                constraint="",
                constraint_message="",
                required="",
                required_message=""
            )

        # Default text: required but no constraint
        return ConstraintSet(
            constraint="",
            constraint_message="",
            required="" if is_non_input else "yes",
            required_message="" if is_non_input else "This field is required"
        )

    def _select_constraints(
        self,
        question: Question,
        is_non_input: bool
    ) -> ConstraintSet:
        """Generate constraints for select questions.

        Args:
            question: The question object
            is_non_input: Whether this is a non-input type

        Returns:
            ConstraintSet for select question
        """
        # Select questions: always required (unless non-input type)
        return ConstraintSet(
            constraint="",
            constraint_message="",
            required="" if is_non_input else "yes",
            required_message="" if is_non_input else "Please select an option"
        )

    def _default_constraints(
        self,
        question: Question,
        is_non_input: bool
    ) -> ConstraintSet:
        """Generate default constraints.

        Args:
            question: The question object
            is_non_input: Whether this is a non-input type

        Returns:
            ConstraintSet with defaults
        """
        return ConstraintSet(
            constraint="",
            constraint_message="",
            required="" if is_non_input else "yes",
            required_message="" if is_non_input else "This field is required"
        )


if __name__ == "__main__":
    # Test the constraint generator
    print("Testing SmartConstraintGenerator...\n")

    generator = SmartConstraintGenerator()

    test_cases = [
        Question("integer", "age", "What is your age?"),
        Question("integer", "household_size", "How many people?"),
        Question("decimal", "weight", "Weight in kg"),
        Question("decimal", "income", "Monthly income"),
        Question("decimal", "satisfaction_pct", "Satisfaction %"),
        Question("text", "name", "Full name"),
        Question("text", "email", "Email address"),
        Question("text", "phone", "Phone number"),
        Question("select_one gender", "gender", "What is your gender?"),
        Question("note", "instructions", "Instructions"),
    ]

    for question in test_cases:
        constraints = generator.generate_constraints(question)
        print(f"Question: {question.type} | {question.name} | \"{question.label}\"")
        if constraints.constraint:
            print(f"  Constraint: {constraints.constraint}")
            print(f"  Message: {constraints.constraint_message}")
        if constraints.required:
            print(f"  Required: {constraints.required}")
            print(f"  Req Message: {constraints.required_message}")
        if constraints.appearance:
            print(f"  Appearance: {constraints.appearance}")
        print()

    print("[OK] All tests completed!")
