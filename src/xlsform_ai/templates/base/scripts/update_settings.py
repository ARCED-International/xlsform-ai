"""Update XLSForm settings sheet (form_title, form_id, version)."""

import sys
from pathlib import Path

# CRITICAL: Add scripts directory to Python path for sibling imports
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    from config import ProjectConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from settings_utils import set_form_settings
except ImportError as exc:
    raise SystemExit(f"Error: {exc}")


def resolve_xlsform_path(file_arg: str = None) -> Path:
    if file_arg:
        return Path(file_arg)
    if CONFIG_AVAILABLE:
        config = ProjectConfig()
        return config.get_full_xlsform_path()
    return Path("survey.xlsx")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Update XLSForm settings sheet.")
    parser.add_argument("--title", help="Form title to set (settings.form_title)")
    parser.add_argument("--id", dest="form_id", help="Form ID to set (settings.form_id)")
    parser.add_argument(
        "--version",
        help=(
            "Version value to set (settings.version). "
            "If omitted, the default formula is enforced."
        ),
    )
    parser.add_argument(
        "--ensure-version-formula",
        action="store_true",
        help="Ensure settings.version uses the default formula even when title/id are unchanged.",
    )
    parser.add_argument("--file", "-f", help="Path to XLSForm file (defaults to config or survey.xlsx)")

    args = parser.parse_args()

    if args.title is None and args.form_id is None and args.version is None and not args.ensure_version_formula:
        print("Error: Provide --title and/or --id and/or --version (or --ensure-version-formula).")
        sys.exit(1)

    xlsform_path = resolve_xlsform_path(args.file)
    if not xlsform_path.exists():
        print(f"Error: XLSForm file not found: {xlsform_path}")
        sys.exit(1)

    ok = set_form_settings(
        xlsform_path,
        form_title=args.title,
        form_id=args.form_id,
        version=args.version,
    )
    if ok:
        print(f"[OK] Updated settings in {xlsform_path.name}")
    else:
        print("[ERROR] Failed to update settings.")
        sys.exit(1)


if __name__ == "__main__":
    main()
