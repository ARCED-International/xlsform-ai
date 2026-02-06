"""Choice List Optimizer - Reuse and standardize choice lists.

This module optimizes choice list creation and reuse by:
1. Detecting standard lists (yes_no, gender, agreement, frequency)
2. Checking for exact matches in existing lists
3. Checking for semantic similarity (using embeddings if available)
4. Creating new lists only when necessary
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChoiceListDecision:
    """Decision about choice list reuse/creation."""
    list_name: str
    reuse_status: str  # "standard", "exact", "similar", "new"
    numeric_codes: List[Dict[str, str]]
    warning: str = ""


class ChoiceListOptimizer:
    """Optimize choice list creation and reuse.

    Implements aggressive choice list reuse to maintain consistency
    across forms and improve data quality.

    Example:
        >>> optimizer = ChoiceListOptimizer()
        >>> decision = optimizer.optimize_choice_list(
        ...     "Yes or No?",
        ...     ["Yes", "No"]
        ... )
        >>> print(decision.list_name)  # "yes_no"
        >>> print(decision.reuse_status)  # "standard"
    """

    # Standard response codes for special values (negative for consistency)
    SPECIAL_CODES = {
        "other": "-96",
        "dont_know": "-99",
        "refused": "-98"
    }

    # Standard reusable choice lists
    STANDARD_LISTS = {
        "yes_no": [
            {"name": "1", "label": "Yes"},
            {"name": "2", "label": "No"}
        ],
        "yes_no_dk_ref": [
            {"name": "1", "label": "Yes"},
            {"name": "2", "label": "No"},
            {"name": "-99", "label": "Don't know"},
            {"name": "-98", "label": "Refused"}
        ],
        "gender": [
            {"name": "1", "label": "Male"},
            {"name": "2", "label": "Female"},
            {"name": "-96", "label": "Other"},
            {"name": "-99", "label": "Don't know"},
            {"name": "-98", "label": "Refused"}
        ],
        "gender_simple": [
            {"name": "1", "label": "Male"},
            {"name": "2", "label": "Female"},
            {"name": "-96", "label": "Other"}
        ],
        "agreement": [
            {"name": "1", "label": "Strongly agree"},
            {"name": "2", "label": "Agree"},
            {"name": "3", "label": "Neutral"},
            {"name": "4", "label": "Disagree"},
            {"name": "5", "label": "Strongly disagree"},
            {"name": "-99", "label": "Don't know"},
            {"name": "-98", "label": "Refused"}
        ],
        "satisfaction": [
            {"name": "1", "label": "Very satisfied"},
            {"name": "2", "label": "Satisfied"},
            {"name": "3", "label": "Neutral"},
            {"name": "4", "label": "Dissatisfied"},
            {"name": "5", "label": "Very dissatisfied"},
            {"name": "-99", "label": "Don't know"},
            {"name": "-98", "label": "Refused"}
        ],
        "frequency": [
            {"name": "1", "label": "Always"},
            {"name": "2", "label": "Often"},
            {"name": "3", "label": "Sometimes"},
            {"name": "4", "label": "Rarely"},
            {"name": "5", "label": "Never"},
            {"name": "-99", "label": "Don't know"},
            {"name": "-98", "label": "Refused"}
        ],
        "yes_no_unsure": [
            {"name": "1", "label": "Yes"},
            {"name": "2", "label": "No"},
            {"name": "-99", "label": "Don't know"}
        ],
    }

    def __init__(self, existing_choices: Optional[Dict[str, List[Dict[str, str]]]] = None):
        """Initialize the optimizer.

        Args:
            existing_choices: Dict of existing choice lists in the form.
                             Keys are list_names, values are lists of choices.
        """
        self.existing_choices = existing_choices or {}

    def optimize_choice_list(
        self,
        question_text: str,
        options: List[str],
        force_new_list: bool = False
    ) -> ChoiceListDecision:
        """Determine whether to reuse or create choice list.

        Strategy:
        1. If force_new_list → create new
        2. Check for standard lists (yes_no, gender, etc.)
        3. Check for exact match in existing lists
        4. Check for semantic similarity
        5. Create new list only if necessary

        Args:
            question_text: Question label
            options: List of choice option labels
            force_new_list: Force creation of new list

        Returns:
            ChoiceListDecision with list_name, reuse_status, numeric_codes

        Example:
            >>> decision = optimizer.optimize_choice_list(
            ...     "Yes or No?",
            ...     ["Yes", "No"]
            ... )
            >>> print(decision.list_name)  # "yes_no"
            >>> print(decision.numeric_codes)
            [{'name': '1', 'label': 'Yes'}, {'name': '2', 'label': 'No'}]
        """
        if force_new_list:
            return self._create_new_list(question_text, options)

        # Normalize option labels for comparison
        option_labels = [opt.strip().lower() for opt in options]

        # Check for standard lists
        standard_match = self._check_standard_lists(option_labels)
        if standard_match:
            return standard_match

        # Check for exact match in existing
        exact_match = self._find_exact_match(option_labels)
        if exact_match:
            return ChoiceListDecision(
                list_name=exact_match,
                reuse_status="exact",
                numeric_codes=self.existing_choices[exact_match],
                warning=""
            )

        # Check for semantic similarity (basic implementation)
        similar_list = self._find_similar_list(option_labels)
        if similar_list:
            return similar_list

        # Create new list with numeric codes
        return self._create_new_list(question_text, options)

    def _check_standard_lists(
        self,
        option_labels: List[str]
    ) -> Optional[ChoiceListDecision]:
        """Check if options match a standard list.

        Args:
            option_labels: Normalized option labels

        Returns:
            ChoiceListDecision if match found, None otherwise
        """
        # Check yes_no
        yes_labels = {"yes", "no"}
        if set(option_labels) == yes_labels:
            return ChoiceListDecision(
                list_name="yes_no",
                reuse_status="standard",
                numeric_codes=self.STANDARD_LISTS["yes_no"],
                warning=""
            )

        # Check yes_no_unsure
        yes_no_unsure_labels = {"yes", "no", "unsure", "don't know", "not sure"}
        if all(label in yes_no_unsure_labels for label in option_labels) and len(option_labels) <= 3:
            # Map options to standard list
            codes = []
            for opt in option_labels:
                if opt == "yes":
                    codes.append({"name": "1", "label": "Yes"})
                elif opt == "no":
                    codes.append({"name": "2", "label": "No"})
                else:
                    codes.append({"name": "3", "label": "Unsure"})
            return ChoiceListDecision(
                list_name="yes_no_unsure",
                reuse_status="standard",
                numeric_codes=codes,
                warning=""
            )

        # Check gender
        gender_keywords = {"male", "female"}
        if any(gender in label for label in option_labels for gender in gender_keywords):
            return ChoiceListDecision(
                list_name="gender_simple",
                reuse_status="standard",
                numeric_codes=self.STANDARD_LISTS["gender_simple"],
                warning=""
            )

        # Check agreement
        agreement_keywords = {"agree", "disagree", "neutral"}
        if sum(1 for label in option_labels
               if any(keyword in label for keyword in agreement_keywords)) >= 2:
            return ChoiceListDecision(
                list_name="agreement",
                reuse_status="standard",
                numeric_codes=self.STANDARD_LISTS["agreement"],
                warning="Using standard agreement scale"
            )

        # Check frequency
        frequency_keywords = {"always", "often", "sometimes", "rarely", "never"}
        if any(keyword in label for label in option_labels for keyword in frequency_keywords):
            return ChoiceListDecision(
                list_name="frequency",
                reuse_status="standard",
                numeric_codes=self.STANDARD_LISTS["frequency"],
                warning="Using standard frequency scale"
            )

        return None

    def _find_exact_match(
        self,
        option_labels: List[str]
    ) -> Optional[str]:
        """Find exact match in existing choice lists.

        Args:
            option_labels: Normalized option labels

        Returns:
            List name if exact match found, None otherwise
        """
        for list_name, choices in self.existing_choices.items():
            # Extract labels from existing choices
            existing_labels = [choice["label"].strip().lower() for choice in choices]

            # Check for exact match
            if set(existing_labels) == set(option_labels):
                return list_name

        return None

    def _find_similar_list(
        self,
        option_labels: List[str]
    ) -> Optional[ChoiceListDecision]:
        """Find semantically similar choice list.

        Args:
            option_labels: Normalized option labels

        Returns:
            ChoiceListDecision if similar list found, None otherwise

        Note: This is a basic implementation. For production, consider
        using embedding-based similarity matching.
        """
        # For now, just check if there's a list with same number of options
        # and some label overlap
        for list_name, choices in self.existing_choices.items():
            existing_labels = [choice["label"].strip().lower() for choice in choices]

            # Check if similar size
            if abs(len(existing_labels) - len(option_labels)) <= 1:
                # Check for label overlap
                overlap = set(existing_labels) & set(option_labels)
                if len(overlap) >= min(len(existing_labels), len(option_labels)) - 1:
                    return ChoiceListDecision(
                        list_name=list_name,
                        reuse_status="similar",
                        numeric_codes=choices,
                        warning=f"Similar list '{list_name}' exists with different labels. Consider reusing."
                    )

        return None

    def _create_new_list(
        self,
        question_text: str,
        options: List[str]
    ) -> ChoiceListDecision:
        """Create new choice list with numeric codes.

        Args:
            question_text: Question label (used to generate list name)
            options: List of choice option labels

        Returns:
            ChoiceListDecision for new list
        """
        # Generate list name from question text
        list_name = self._generate_list_name(question_text)

        # Generate numeric codes
        numeric_codes = [
            {"name": str(i + 1), "label": opt.strip()}
            for i, opt in enumerate(options)
        ]

        # Check for special response options and assign negative codes
        for i, code in enumerate(numeric_codes):
            label_lower = code["label"].lower()

            # Check for "Other" option
            if any(kw in label_lower for kw in ["other", "other (specify)", "none of the above"]):
                numeric_codes[i]["name"] = self.SPECIAL_CODES["other"]
            # Check for "Don't know" option
            elif any(kw in label_lower for kw in ["don't know", "dont know", "not sure", "unsure"]):
                numeric_codes[i]["name"] = self.SPECIAL_CODES["dont_know"]
            # Check for "Refused" option
            elif any(kw in label_lower for kw in ["refused", "decline", "prefer not to say"]):
                numeric_codes[i]["name"] = self.SPECIAL_CODES["refused"]

        return ChoiceListDecision(
            list_name=list_name,
            reuse_status="new",
            numeric_codes=numeric_codes,
            warning=""
        )

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
            'is', 'are', 'the', 'a', 'an', 'of'
        ]

        # Extract key words
        words = question_text.lower().replace('?', '').split()
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

    def get_standard_lists(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all standard choice lists.

        Returns:
            Dict of standard choice lists
        """
        return self.STANDARD_LISTS.copy()


if __name__ == "__main__":
    # Test the optimizer
    print("Testing ChoiceListOptimizer...\n")

    optimizer = ChoiceListOptimizer()

    test_cases = [
        ("Yes or No?", ["Yes", "No"]),
        ("What is your gender?", ["Male", "Female", "Other"]),
        ("Rate your agreement", ["Strongly agree", "Agree", "Neutral", "Disagree", "Strongly disagree"]),
        ("How often?", ["Always", "Often", "Sometimes", "Rarely", "Never"]),
        ("Select crops", ["Maize", "Beans", "Rice", "Sorghum"]),
    ]

    for question, options in test_cases:
        decision = optimizer.optimize_choice_list(question, options)
        print(f"Question: {question}")
        print(f"  List Name: {decision.list_name}")
        print(f"  Reuse Status: {decision.reuse_status}")
        print(f"  Numeric Codes: {len(decision.numeric_codes)} options")
        if decision.warning:
            print(f"  Warning: {decision.warning}")
        print()

    print("[OK] All tests completed!")
