"""Task complexity analysis for smart parallel execution routing."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import openpyxl


@dataclass
class TaskComplexity:
    """Task complexity metrics.

    Attributes:
        question_count: Number of questions in form
        file_size_mb: File size in megabytes
        page_count: Estimated page count (for PDFs)
        has_select_questions: Whether form has select_one/select_multiple
        has_constraints: Whether form has constraint formulas
        has_relevance: Whether form has relevance logic
        has_repeats: Whether form has repeat groups
        estimated_time_minutes: Estimated processing time
        requires_parallel: Whether parallel execution is recommended
        recommended_agents: List of sub-agents to use
    """
    question_count: int
    file_size_mb: float
    page_count: int
    has_select_questions: bool
    has_constraints: bool
    has_relevance: bool
    has_repeats: bool
    estimated_time_minutes: int
    requires_parallel: bool
    recommended_agents: List[str]

    def __str__(self) -> str:
        """Return human-readable complexity summary."""
        level = "Low" if self.question_count < 30 else "Medium" if self.question_count < 75 else "High"
        return (
            f"Complexity: {level} ({self.question_count} questions, "
            f"{self.page_count} pages, {self.file_size_mb:.2f} MB)"
        )


class ComplexityAnalyzer:
    """Analyzes task complexity for smart routing to parallel execution.

    Thresholds for triggering parallel execution:
    - Questions: >= 50
    - Pages: >= 10
    - File size: >= 1 MB
    """

    # Default thresholds for triggering parallel execution
    QUESTION_THRESHOLD = 50
    PAGE_THRESHOLD = 10
    SIZE_THRESHOLD_MB = 1.0

    def __init__(
        self,
        question_threshold: int = QUESTION_THRESHOLD,
        page_threshold: int = PAGE_THRESHOLD,
        size_threshold_mb: float = SIZE_THRESHOLD_MB,
    ):
        """Initialize analyzer with custom thresholds.

        Args:
            question_threshold: Minimum questions to trigger parallel
            page_threshold: Minimum pages to trigger parallel
            size_threshold_mb: Minimum file size in MB to trigger parallel
        """
        self.question_threshold = question_threshold
        self.page_threshold = page_threshold
        self.size_threshold_mb = size_threshold_mb

    def analyze_xlsform_file(self, xlsx_path: Path) -> TaskComplexity:
        """Analyze XLSForm file and return complexity metrics.

        Args:
            xlsx_path: Path to XLSForm Excel file

        Returns:
            TaskComplexity object with metrics
        """
        if not xlsx_path.exists():
            raise FileNotFoundError(f"XLSForm file not found: {xlsx_path}")

        # Get file size
        file_size_mb = xlsx_path.stat().st_size / (1024 * 1024)

        # Load workbook and analyze
        try:
            wb = openpyxl.load_workbook(xlsx_path, data_only=True)
            survey_sheet = wb["survey"]

            question_count = 0
            has_select_questions = False
            has_constraints = False
            has_relevance = False
            has_repeats = False

            # Analyze survey sheet
            for row_idx, row in enumerate(survey_sheet.iter_rows(values_only=True), 1):
                if row_idx == 1:  # Skip header row
                    continue

                # Get question type (column 2 in XLSForm)
                if len(row) > 1:
                    question_type = row[1]
                    if question_type and question_type != "begin" and question_type != "end":
                        question_count += 1

                        # Check for select questions
                        if question_type and (
                            "select_one" in str(question_type) or
                            "select_multiple" in str(question_type)
                        ):
                            has_select_questions = True

                        # Check for constraints (column 4)
                        if len(row) > 3:
                            constraint = row[3]
                            if constraint:
                                has_constraints = True

                        # Check for relevance (column 5)
                        if len(row) > 4:
                            relevance = row[4]
                            if relevance:
                                has_relevance = True

                # Check for repeat groups (type column)
                if len(row) > 1:
                    if row[1] and "begin repeat" in str(row[1]).lower():
                        has_repeats = True

            wb.close()

            # Estimate processing time (rough heuristic)
            base_time = 1  # 1 minute base
            per_question_time = 0.05  # 3 seconds per question
            complexity_multiplier = 1.5 if has_select_questions else 1.0
            estimated_time = int(
                (base_time + (question_count * per_question_time)) *
                complexity_multiplier
            )

            # Determine if parallel execution is needed
            requires_parallel = (
                question_count >= self.question_threshold or
                file_size_mb >= self.size_threshold_mb
            )

            # Recommend sub-agents based on complexity
            recommended_agents = []
            if has_constraints or has_select_questions:
                recommended_agents.append("validation-agent")
            if question_count > 20:
                recommended_agents.append("schema-agent")
            if requires_parallel:
                recommended_agents.insert(0, "import-agent")  # For chunking

            return TaskComplexity(
                question_count=question_count,
                file_size_mb=file_size_mb,
                page_count=0,  # Not applicable for XLSForm
                has_select_questions=has_select_questions,
                has_constraints=has_constraints,
                has_relevance=has_relevance,
                has_repeats=has_repeats,
                estimated_time_minutes=estimated_time,
                requires_parallel=requires_parallel,
                recommended_agents=recommended_agents,
            )

        except Exception as e:
            # Fallback to basic analysis if Excel reading fails
            return TaskComplexity(
                question_count=0,
                file_size_mb=file_size_mb,
                page_count=0,
                has_select_questions=False,
                has_constraints=False,
                has_relevance=False,
                has_repeats=False,
                estimated_time_minutes=2,
                requires_parallel=file_size_mb >= self.size_threshold_mb,
                recommended_agents=[],
            )

    def analyze_pdf_file(self, pdf_path: Path) -> TaskComplexity:
        """Analyze PDF file and estimate complexity for import.

        Args:
            pdf_path: Path to PDF file

        Returns:
            TaskComplexity object with estimated metrics
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Get file size
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)

        # Estimate pages from file size (rough heuristic: 1 page ≈ 100-500 KB)
        # Using average of 250 KB per page
        estimated_pages = max(1, int(file_size_mb * 1024 / 250))

        # Estimate questions (rough heuristic: 3-5 questions per page)
        min_questions = estimated_pages * 3
        max_questions = estimated_pages * 5
        estimated_questions = (min_questions + max_questions) // 2

        # Estimate processing time
        base_time = 2  # 2 minutes for PDF parsing
        per_page_time = 0.5  # 30 seconds per page
        estimated_time = int(base_time + (estimated_pages * per_page_time))

        # Determine if parallel execution is needed
        requires_parallel = (
            estimated_questions >= self.question_threshold or
            estimated_pages >= self.page_threshold or
            file_size_mb >= self.size_threshold_mb
        )

        # Recommend sub-agents
        recommended_agents = ["import-agent"]
        if estimated_questions > 30:
            recommended_agents.append("validation-agent")
        if requires_parallel:
            recommended_agents.append("schema-agent")

        return TaskComplexity(
            question_count=estimated_questions,
            file_size_mb=file_size_mb,
            page_count=estimated_pages,
            has_select_questions=True,  # Likely in PDF
            has_constraints=False,  # Unknown until parsed
            has_relevance=False,  # Unknown until parsed
            has_repeats=False,  # Unknown until parsed
            estimated_time_minutes=estimated_time,
            requires_parallel=requires_parallel,
            recommended_agents=recommended_agents,
        )

    def get_execution_plan(
        self,
        complexity: TaskComplexity,
        user_override: Optional[str] = None,
    ) -> Dict:
        """Get execution plan based on complexity analysis.

        Args:
            complexity: TaskComplexity object from analysis
            user_override: User's preference ("parallel", "sequential", or None for auto)

        Returns:
            Dict with execution plan including strategy, chunks, and agents
        """
        # Determine execution mode
        if user_override == "parallel":
            execution_mode = "parallel"
        elif user_override == "sequential":
            execution_mode = "sequential"
        else:
            # Auto-detect based on complexity
            execution_mode = "parallel" if complexity.requires_parallel else "sequential"

        # Calculate parallel chunks if needed
        chunks = []
        if execution_mode == "parallel":
            if complexity.page_count > 0:
                # PDF import: chunk by pages
                chunk_size = max(5, complexity.page_count // 5)  # 5 chunks max
                pages_per_chunk = complexity.page_count // 5
                for i in range(0, complexity.page_count, pages_per_chunk):
                    end_page = min(i + pages_per_chunk, complexity.page_count)
                    chunks.append({
                        "type": "pages",
                        "start": i + 1,
                        "end": end_page,
                        "estimated_questions": complexity.question_count // 5,
                    })
            elif complexity.question_count > 0:
                # XLSForm with many questions: chunk by question count
                questions_per_chunk = max(10, complexity.question_count // 5)
                for i in range(0, complexity.question_count, questions_per_chunk):
                    end_q = min(i + questions_per_chunk, complexity.question_count)
                    chunks.append({
                        "type": "questions",
                        "start": i + 1,
                        "end": end_q,
                    })

        return {
            "mode": execution_mode,
            "complexity": complexity,
            "strategy": self._get_strategy_description(execution_mode, complexity),
            "chunks": chunks,
            "estimated_time_minutes": complexity.estimated_time_minutes,
            "recommended_agents": complexity.recommended_agents,
            "parallel_speedup": len(chunks) if execution_mode == "parallel" else 1,
        }

    def _get_strategy_description(self, mode: str, complexity: TaskComplexity) -> str:
        """Get human-readable strategy description.

        Args:
            mode: Execution mode ("parallel" or "sequential")
            complexity: TaskComplexity object

        Returns:
            Strategy description string
        """
        if mode == "parallel":
            if complexity.page_count > 0:
                return f"Parallel PDF import ({complexity.page_count} pages in {max(1, complexity.page_count // 5)} chunks)"
            else:
                return f"Parallel processing ({complexity.question_count} questions in {max(1, complexity.question_count // 50)} chunks)"
        else:
            return "Sequential processing (task complexity below threshold)"


def analyze_task(file_path: Path, user_preference: Optional[str] = None) -> Dict:
    """Convenience function to analyze a file and get execution plan.

    Args:
        file_path: Path to file (PDF or XLSForm)
        user_preference: User's preference ("parallel", "sequential", or None)

    Returns:
        Execution plan dict
    """
    analyzer = ComplexityAnalyzer()

    # Detect file type and analyze
    if file_path.suffix.lower() == ".pdf":
        complexity = analyzer.analyze_pdf_file(file_path)
    elif file_path.suffix.lower() in [".xlsx", ".xls"]:
        complexity = analyzer.analyze_xlsform_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    return analyzer.get_execution_plan(complexity, user_preference)
