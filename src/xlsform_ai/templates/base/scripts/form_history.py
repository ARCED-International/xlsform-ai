#!/usr/bin/env python3
"""Manage XLSForm history snapshots and rollback operations."""

import argparse
import sys
from pathlib import Path


# CRITICAL: Add scripts directory to Python path for sibling imports
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    from config import ProjectConfig
    CONFIG_AVAILABLE = True
except Exception:
    CONFIG_AVAILABLE = False

try:
    from log_activity import ActivityLogger
    LOGGING_AVAILABLE = True
except Exception:
    LOGGING_AVAILABLE = False

from history_manager import WorkbookHistoryManager


def _resolve_xlsform_path(file_arg: str = None) -> Path:
    if file_arg:
        return Path(file_arg).resolve()
    if CONFIG_AVAILABLE:
        config = ProjectConfig()
        return config.get_full_xlsform_path().resolve()
    return Path("survey.xlsx").resolve()


def _log_revert(action: str, description: str, details: str) -> None:
    if not LOGGING_AVAILABLE:
        return
    try:
        logger = ActivityLogger()
        logger.log_action(action_type=action, description=description, details=details)
    except Exception:
        pass


def _print_snapshot_table(records):
    if not records:
        print("No snapshots found.")
        return

    print("Revision History (newest first):")
    print("revision_id           timestamp                     action_type      description")
    print("-" * 92)
    for record in records:
        revision_id = record.get("revision_id", "")
        timestamp = record.get("timestamp", "")
        action_type = record.get("action_type", "")
        description = record.get("description", "")
        print(f"{revision_id:20} {timestamp:28} {action_type:15} {description}")


def cmd_list(args) -> int:
    xlsform_path = _resolve_xlsform_path(args.file)
    manager = WorkbookHistoryManager(xlsform_path=xlsform_path)
    records = manager.list_snapshots(limit=args.limit)
    _print_snapshot_table(records)
    return 0


def cmd_checkpoint(args) -> int:
    xlsform_path = _resolve_xlsform_path(args.file)
    if not xlsform_path.exists():
        print(f"Error: XLSForm file not found: {xlsform_path}")
        return 1

    manager = WorkbookHistoryManager(xlsform_path=xlsform_path)
    try:
        with manager.edit_lock():
            record = manager.create_snapshot(
                action_type="checkpoint",
                description=f"Manual checkpoint: {args.label}",
                details=args.label,
                command="/xlsform-revert --checkpoint",
            )
    except Exception as exc:
        print(f"Error: Could not create checkpoint: {exc}")
        return 1
    print(f"[OK] Checkpoint created: {record['revision_id']}")
    return 0


def _restore_by_revision(manager: WorkbookHistoryManager, revision_id: str, dry_run: bool) -> int:
    snapshot = manager.get_snapshot(revision_id)
    if not snapshot:
        print(f"Error: Revision not found: {revision_id}")
        return 1

    if dry_run:
        print("Dry run only. Restore target:")
        print(f"  revision_id: {snapshot.get('revision_id')}")
        print(f"  timestamp: {snapshot.get('timestamp')}")
        print(f"  action_type: {snapshot.get('action_type')}")
        print(f"  description: {snapshot.get('description')}")
        print(f"  snapshot_path: {snapshot.get('snapshot_path')}")
        return 0

    try:
        with manager.edit_lock():
            result = manager.restore_snapshot(revision_id, create_pre_restore_snapshot=True)
    except Exception as exc:
        print(f"Error: Restore failed: {exc}")
        return 1
    pre_restore = result.get("pre_restore_snapshot")
    if pre_restore:
        print(f"[OK] Pre-restore snapshot: {pre_restore['revision_id']}")
    print(f"[OK] Restored to revision: {revision_id}")
    _log_revert(
        action="revert",
        description=f"Restored workbook to revision {revision_id}",
        details=f"Revision: {revision_id}",
    )
    return 0


def cmd_restore(args) -> int:
    xlsform_path = _resolve_xlsform_path(args.file)
    if not xlsform_path.exists():
        print(f"Error: XLSForm file not found: {xlsform_path}")
        return 1
    manager = WorkbookHistoryManager(xlsform_path=xlsform_path)
    return _restore_by_revision(manager, args.revision, args.dry_run)


def cmd_restore_last(args) -> int:
    xlsform_path = _resolve_xlsform_path(args.file)
    if not xlsform_path.exists():
        print(f"Error: XLSForm file not found: {xlsform_path}")
        return 1

    manager = WorkbookHistoryManager(xlsform_path=xlsform_path)
    latest = manager.get_latest_snapshot(include_pre_restore=False)
    if not latest:
        print("No restorable snapshots found.")
        return 1
    return _restore_by_revision(manager, latest["revision_id"], args.dry_run)


def cmd_undo(args) -> int:
    xlsform_path = _resolve_xlsform_path(args.file)
    if not xlsform_path.exists():
        print(f"Error: XLSForm file not found: {xlsform_path}")
        return 1

    manager = WorkbookHistoryManager(xlsform_path=xlsform_path)
    latest = manager.get_latest_snapshot(include_pre_restore=True)
    if not latest:
        print("No snapshots found for undo.")
        return 1
    return _restore_by_revision(manager, latest["revision_id"], args.dry_run)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="XLSForm history and rollback utility")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    parser_list = subparsers.add_parser("list", help="List available snapshots")
    parser_list.add_argument("--file", "-f", help="Path to XLSForm file")
    parser_list.add_argument("--limit", type=int, default=20, help="Max snapshots to display")
    parser_list.set_defaults(func=cmd_list)

    parser_checkpoint = subparsers.add_parser("checkpoint", help="Create manual checkpoint snapshot")
    parser_checkpoint.add_argument("label", help="Checkpoint label")
    parser_checkpoint.add_argument("--file", "-f", help="Path to XLSForm file")
    parser_checkpoint.set_defaults(func=cmd_checkpoint)

    parser_restore = subparsers.add_parser("restore", help="Restore specific revision")
    parser_restore.add_argument("--revision", "-r", required=True, help="Revision ID to restore")
    parser_restore.add_argument("--file", "-f", help="Path to XLSForm file")
    parser_restore.add_argument("--dry-run", action="store_true", help="Preview restore target only")
    parser_restore.set_defaults(func=cmd_restore)

    parser_restore_last = subparsers.add_parser("restore-last", help="Restore from latest user snapshot")
    parser_restore_last.add_argument("--file", "-f", help="Path to XLSForm file")
    parser_restore_last.add_argument("--dry-run", action="store_true", help="Preview restore target only")
    parser_restore_last.set_defaults(func=cmd_restore_last)

    parser_undo = subparsers.add_parser("undo", help="Undo using latest snapshot (including pre-restore)")
    parser_undo.add_argument("--file", "-f", help="Path to XLSForm file")
    parser_undo.add_argument("--dry-run", action="store_true", help="Preview restore target only")
    parser_undo.set_defaults(func=cmd_undo)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
