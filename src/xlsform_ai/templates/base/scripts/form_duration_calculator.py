"""Form Duration Calculator - Add automatic form duration tracking.

This module adds a form duration calculation field to XLSForm metadata
to track how long enumerators spend on each form submission.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DurationField:
    """Form duration calculation field definition."""
    field_type: str
    name: str
    label: str
    calculation: str
    bind: Dict[str, str]


class FormDurationCalculator:
    """Add form duration calculation to XLSForm metadata.

    Automatically adds a calculate field that tracks the time between
    form start and end in minutes.

    Example:
        >>> calculator = FormDurationCalculator()
        >>> if calculator.has_start_end_metadata(worksheet):
        ...     calculator.add_duration_to_form(worksheet, header_row)
    """

    def __init__(self, duration_field_name: str = "form_duration_minutes"):
        """Initialize the calculator.

        Args:
            duration_field_name: Name for the duration field
        """
        self.duration_field_name = duration_field_name

        # Metadata field types to look for
        self.metadata_types = {
            'start', 'end', 'today', 'deviceid', 'subscriberid',
            'simserial', 'phonenumber', 'username', 'audit'
        }

    def has_start_end_metadata(self, ws) -> bool:
        """Check if form has start and end metadata fields.

        Args:
            ws: openpyxl worksheet object

        Returns:
            True if both start and end found

        Example:
            >>> if calculator.has_start_end_metadata(worksheet):
            ...     calculator.add_duration_to_form(worksheet, header_row)
        """
        has_start = False
        has_end = False

        # Scan through rows looking for start/end
        for row_idx in range(2, min(ws.max_row + 1, 100)):  # Check first 100 rows
            cell_type = ws.cell(row_idx, 1).value  # Type column
            cell_name = ws.cell(row_idx, 2).value  # Name column

            if cell_type:
                cell_type_lower = str(cell_type).lower()
                cell_name_lower = str(cell_name).lower() if cell_name else ""

                if cell_type_lower == "start" or "start" in cell_name_lower:
                    has_start = True
                elif cell_type_lower == "end" or "end" in cell_name_lower:
                    has_end = True

                # Early exit if both found
                if has_start and has_end:
                    return True

        return has_start and has_end

    def create_duration_field(self) -> DurationField:
        """Create duration calculation field.

        Returns:
            DurationField with field definition

        Example:
            >>> field = calculator.create_duration_field()
            >>> print(field.calculation)
            round((decimal-time-end() - decimal-time-start()) * 1440)
        """
        return DurationField(
            field_type="calculate",
            name=self.duration_field_name,
            label="Form Duration (minutes)",
            calculation="round((decimal-time-end() - decimal-time-start()) * 1440)",
            bind={
                "type": "calculate"
            }
        )

    def add_duration_to_form(
        self,
        ws,
        header_row: int,
        columns: Optional[Dict[str, int]] = None
    ) -> Optional[int]:
        """Add duration calculation after metadata section.

        Args:
            ws: openpyxl worksheet
            header_row: Header row number
            columns: Optional column mapping (type=1, name=2, label=3, etc.)

        Returns:
            Row where duration was added, or None if not added

        Example:
            >>> row = calculator.add_duration_to_form(ws, 1)
            >>> print(f"Added duration field at row {row}")
        """
        if not self.has_start_end_metadata(ws):
            return None  # Don't add if no start/end

        # Default column mapping
        if columns is None:
            columns = {
                "type": 1,
                "name": 2,
                "label": 3,
                "calculation": 6
            }

        # Find end of metadata section
        metadata_end_row = self._find_metadata_end(ws, header_row)

        # Insert new row after metadata
        ws.insert_rows(metadata_end_row + 1)

        # Create duration field
        duration_field = self.create_duration_field()

        # Write to sheet
        ws.cell(metadata_end_row + 1, columns["type"], duration_field.field_type)
        ws.cell(metadata_end_row + 1, columns["name"], duration_field.name)
        ws.cell(metadata_end_row + 1, columns["label"], duration_field.label)
        ws.cell(metadata_end_row + 1, columns["calculation"], duration_field.calculation)

        return metadata_end_row + 1

    def _find_metadata_end(self, ws, header_row: int) -> int:
        """Find the last metadata field row.

        Args:
            ws: openpyxl worksheet
            header_row: Header row number

        Returns:
            Row number of last metadata field
        """
        last_metadata_row = header_row

        for row_idx in range(header_row + 1, ws.max_row + 1):
            cell_type = ws.cell(row_idx, 1).value
            cell_name = ws.cell(row_idx, 2).value

            if not cell_type and not cell_name:
                # Empty row - end of section
                break

            cell_type_str = str(cell_type).lower() if cell_type else ""

            # Check if this is a metadata type
            if cell_type_str in self.metadata_types:
                last_metadata_row = row_idx
            elif cell_type_str and not cell_type_str.startswith("begin"):
                # Reached first non-metadata question
                break

        return last_metadata_row

    def update_duration_field(
        self,
        ws,
        header_row: int,
        columns: Optional[Dict[str, int]] = None
    ) -> bool:
        """Update existing duration field if present.

        Args:
            ws: openpyxl worksheet
            header_row: Header row number
            columns: Optional column mapping

        Returns:
            True if updated, False if not found
        """
        if columns is None:
            columns = {
                "type": 1,
                "name": 2,
                "calculation": 6
            }

        # Search for existing duration field
        for row_idx in range(header_row + 1, ws.max_row + 1):
            cell_name = ws.cell(row_idx, columns["name"]).value

            if cell_name and str(cell_name) == self.duration_field_name:
                # Found it - update calculation
                duration_field = self.create_duration_field()
                ws.cell(row_idx, columns["calculation"], duration_field.calculation)
                return True

        return False


if __name__ == "__main__":
    # Test the calculator
    print("Testing FormDurationCalculator...\n")

    calculator = FormDurationCalculator()

    # Test create_duration_field
    print("Test 1: Create Duration Field")
    field = calculator.create_duration_field()
    print(f"  Type: {field.field_type}")
    print(f"  Name: {field.name}")
    print(f"  Label: {field.label}")
    print(f"  Calculation: {field.calculation}")

    # Test with mock worksheet (conceptual)
    print("\nTest 2: Metadata Detection")
    print("  Note: Full worksheet testing requires openpyxl with actual data")
    print("  The calculator checks for 'start' and 'end' metadata fields")
    print("  and adds duration calculation after them")

    print("\n[OK] All tests completed!")
    print("\nUsage Example:")
    print("  calculator = FormDurationCalculator()")
    print("  if calculator.has_start_end_metadata(ws):")
    print("      calculator.add_duration_to_form(ws, header_row)")
