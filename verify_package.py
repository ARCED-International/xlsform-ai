#!/usr/bin/env python
"""Verify that templates are included in the installed package."""

import os
import sys
from pathlib import Path

def check_installed_package():
    """Check what's in the installed xlsform_ai package."""

    try:
        import xlsform_ai
    except ImportError:
        print("[X] xlsform_ai package not found!")
        return False

    pkg_dir = Path(xlsform_ai.__file__).parent
    print(f"[OK] Package location: {pkg_dir}")
    print()

    # Check for templates directory
    templates_dir = pkg_dir / "templates"
    if templates_dir.exists():
        print(f"[OK] templates/ directory exists")
        print(f"    Contents: {list(templates_dir.iterdir())}")
    else:
        print(f"[X] templates/ directory NOT found")
        print(f"    Package contents:")
        for item in sorted(pkg_dir.iterdir()):
            print(f"      - {item.name}")
        return False

    # Check for Excel template files
    print()
    print("Searching for .xlsx files...")
    xlsx_files = list(pkg_dir.rglob("*.xlsx"))
    if xlsx_files:
        print(f"[OK] Found {len(xlsx_files)} Excel file(s):")
        for f in xlsx_files:
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.relative_to(pkg_dir)} ({size_kb:.1f} KB)")
    else:
        print(f"[X] No .xlsx files found in package!")

    return len(xlsx_files) > 0

if __name__ == "__main__":
    print("Verifying xlsform_ai package installation...\n")
    success = check_installed_package()
    sys.exit(0 if success else 1)
