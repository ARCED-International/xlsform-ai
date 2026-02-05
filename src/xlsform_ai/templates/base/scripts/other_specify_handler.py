"""Other Specify Handler - Automatically detect and handle 'Other' choices.

This module automatically detects "Other" choice options and creates
"Other specify" follow-up questions with proper relevance logic.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Question:
    """Question information."""
    type: str
    name: str
    label: str
    choices: Optional[List[Dict[str, str]]] = None


class OtherSpecifyHandler:
    """Automatically detect and handle 'Other' choices with specify fields.

    When a select question includes an "Other" option, this handler
    automatically creates a follow-up text question with relevance
    logic to show only when "Other" is selected.

    Example:
        >>> handler = OtherSpecifyHandler()
        >>> choices = [
        ...     {"name": "1", "label": "Male"},
        ...     {"name": "2", "label": "Female"},
        ...     {"name": "99", "label": "Other (specify)"}
        ... ]
        >>> has_other = handler.detect_other_choice(choices)
        >>> print(has_other)  # True
    """

    # Keywords that indicate an "Other" option
    OTHER_KEYWORDS = [
        "other",
        "other (specify)",
        "other, please specify",
        "other specify",
        "none of the above"
    ]

    # Standard special response codes (negative for consistency)
    SPECIAL_CODES = {
        "other": "-96",
        "dont_know": "-99",
        "refused": "-98"
    }

    # Default code to use for "Other" option
    OTHER_CODE = "-96"

    def __init__(self):
        """Initialize the handler."""
        pass

    def detect_other_choice(self, choices: List[Dict[str, str]]) -> bool:
        """Detect if choice list contains 'Other' option.

        Args:
            choices: List of choice dicts with 'name' and 'label' keys

        Returns:
            True if 'Other' detected

        Example:
            >>> choices = [
            ...     {"name": "1", "label": "Male"},
            ...     {"name": "99", "label": "Other (specify)"}
            ... ]
            >>> handler.detect_other_choice(choices)
            True
        """
        if not choices:
            return False

        choice_labels = [choice.get("label", "").lower() for choice in choices]
        choice_names = [choice.get("name", "").lower() for choice in choices]

        # Check labels
        for label in choice_labels:
            if any(keyword in label for keyword in self.OTHER_KEYWORDS):
                return True

        # Check names
        for name in choice_names:
            if "other" in name or name == self.OTHER_CODE:
                return True

        return False

    def find_other_choice(self, choices: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Find the 'Other' choice in the list.

        Args:
            choices: List of choice dicts

        Returns:
            The "Other" choice dict, or None if not found
        """
        if not choices:
            return None

        for choice in choices:
            label = choice.get("label", "").lower()
            name = choice.get("name", "")

            # Check label
            if any(keyword in label for keyword in self.OTHER_KEYWORDS):
                return choice

            # Check name
            if "other" in name.lower() or name == self.OTHER_CODE:
                return choice

        return None

    def create_other_specify_question(
        self,
        parent_question: Question,
        other_choice_name: str
    ) -> Question:
        """Create 'Other specify' follow-up question.

        Args:
            parent_question: The parent select question
            other_choice_name: The choice name for 'Other' (e.g., "99")

        Returns:
            Question object for 'Other specify' follow-up

        Example:
            >>> parent = Question("select_one gender", "gender", "What is your gender?")
            >>> other_q = handler.create_other_specify_question(parent, "99")
            >>> print(other_q.relevance)  # "${gender} = '99'"
        """
        # Generate question name
        other_name = f"{parent_question.name}_other"

        # Generate label
        other_label = "Please specify (Other)"

        # Set relevance to show only when 'Other' selected
        relevance = f"${{{parent_question.name}}} = '{other_choice_name}'"

        return Question(
            type="text",
            name=other_name,
            label=other_label,
            choices=None
        )

    def process_question_with_other(
        self,
        question: Question,
        choices: List[Dict[str, str]]
    ) -> List[Question]:
        """Process a select question and add 'Other specify' if needed.

        Args:
            question: The select question to check
            choices: List of choice dicts

        Returns:
            List of questions (original + other_specify if needed)

        Example:
            >>> choices = [
            ...     {"name": "1", "label": "Male"},
            ...     {"name": "2", "label": "Female"},
            ...     {"name": "99", "label": "Other (specify)"}
            ... ]
            >>> question = Question("select_one gender", "gender", "Gender")
            >>> questions = handler.process_question_with_other(question, choices)
            >>> len(questions)  # 2 (original + other_specify)
        """
        questions = [question]

        if self.detect_other_choice(choices):
            # Find the 'Other' choice
            other_choice = self.find_other_choice(choices)

            if other_choice:
                # Get the choice name (default to 99 if not set)
                other_choice_name = other_choice.get("name", self.OTHER_CODE)

                # Create other_specify follow-up
                other_question = self.create_other_specify_question(
                    question, other_choice_name
                )
                other_question.relevance = f"${{{question.name}}} = '{other_choice_name}'"
                questions.append(other_question)

        return questions

    def add_other_specify_to_choices(
        self,
        choices: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Ensure 'Other' option exists in choices and has proper code.

        Args:
            choices: List of choice dicts

        Returns:
            Updated list of choices with "Other" option added if missing

        Example:
            >>> choices = [
            ...     {"name": "1", "label": "Male"},
            ...     {"name": "2", "label": "Female"}
            ... ]
            >>> updated = handler.add_other_specify_to_choices(choices)
            >>> len(updated)  # 3 (Male, Female, Other)
        """
        # Check if "Other" already exists
        if self.detect_other_choice(choices):
            # Ensure it has code 99
            for choice in choices:
                label = choice.get("label", "").lower()
                if any(keyword in label for keyword in self.OTHER_KEYWORDS):
                    if choice.get("name") != self.OTHER_CODE:
                        choice["name"] = self.OTHER_CODE
            return choices

        # Add "Other" option if not present
        updated_choices = choices.copy()
        updated_choices.append({
            "name": self.OTHER_CODE,
            "label": "Other (specify)"
        })

        return updated_choices


if __name__ == "__main__":
    # Test the handler
    print("Testing OtherSpecifyHandler...\n")

    handler = OtherSpecifyHandler()

    # Test detection
    choices_with_other = [
        {"name": "1", "label": "Male"},
        {"name": "2", "label": "Female"},
        {"name": "99", "label": "Other (specify)"}
    ]

    choices_without_other = [
        {"name": "1", "label": "Male"},
        {"name": "2", "label": "Female"}
    ]

    print("Test 1: Detection")
    print(f"  With Other: {handler.detect_other_choice(choices_with_other)}")  # True
    print(f"  Without Other: {handler.detect_other_choice(choices_without_other)}")  # False

    # Test finding other choice
    print("\nTest 2: Find Other Choice")
    other_choice = handler.find_other_choice(choices_with_other)
    print(f"  Found: {other_choice}")

    # Test creating other specify question
    print("\nTest 3: Create Other Specify Question")
    parent_question = Question(
        type="select_one gender",
        name="gender",
        label="What is your gender?"
    )

    other_question = handler.create_other_specify_question(
        parent_question,
        "99"
    )

    print(f"  Parent: {parent_question.name}")
    print(f"  Other: {other_question.name}")
    print(f"  Relevance: {other_question.relevance}")

    # Test processing
    print("\nTest 4: Process Question with Other")
    questions = handler.process_question_with_other(
        parent_question,
        choices_with_other
    )

    print(f"  Total questions: {len(questions)}")
    for i, q in enumerate(questions):
        print(f"    {i+1}. {q.name} ({q.type})")

    # Test adding other to choices
    print("\nTest 5: Add Other to Choices")
    updated_choices = handler.add_other_specify_to_choices(choices_without_other)
    print(f"  Original: {len(choices_without_other)} choices")
    print(f"  Updated: {len(updated_choices)} choices")
    print(f"  Choices: {[c['label'] for c in updated_choices]}")

    print("\n[OK] All tests completed!")
