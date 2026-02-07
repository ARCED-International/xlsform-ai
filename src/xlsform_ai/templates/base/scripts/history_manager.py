"""Workbook history manager for safe snapshots and rollback."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple


LOCK_FILENAME = ".edit.lock"
MANIFEST_FILENAME = "history.jsonl"


def _utc_now_iso() -> str:
    """Return UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _file_sha256(path: Path) -> str:
    """Compute SHA-256 hash for a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _normalized_path(path: Path) -> str:
    """Normalize path for robust comparisons."""
    return str(path.resolve()).lower()


class WorkbookHistoryManager:
    """Manage immutable snapshots and rollback for XLSForm files."""

    def __init__(self, xlsform_path: Path, project_dir: Optional[Path] = None):
        self.xlsform_path = Path(xlsform_path).resolve()
        self.project_dir = Path(project_dir).resolve() if project_dir else self.xlsform_path.parent
        self.history_dir = self.project_dir / ".xlsform-ai" / "history"
        self.snapshots_dir = self.history_dir / "snapshots"
        self.manifest_path = self.history_dir / MANIFEST_FILENAME
        self.lock_path = self.history_dir / LOCK_FILENAME

    def ensure_dirs(self) -> None:
        """Create history directories if needed."""
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def acquire_lock(self, timeout_seconds: float = 30.0, poll_seconds: float = 0.25) -> None:
        """Acquire exclusive edit lock for the workbook."""
        self.ensure_dirs()
        started = time.time()
        payload = {
            "pid": os.getpid(),
            "file": str(self.xlsform_path),
            "timestamp": _utc_now_iso(),
        }
        body = json.dumps(payload, ensure_ascii=True)

        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, body.encode("utf-8"))
                finally:
                    os.close(fd)
                return
            except FileExistsError:
                if time.time() - started >= timeout_seconds:
                    details = ""
                    try:
                        details = self.lock_path.read_text(encoding="utf-8")
                    except Exception:
                        details = "<unreadable lock details>"
                    raise TimeoutError(
                        f"Could not acquire workbook lock within {timeout_seconds:.1f}s. "
                        f"Lock: {self.lock_path}. Details: {details}"
                    )
                time.sleep(poll_seconds)

    def release_lock(self) -> None:
        """Release edit lock if this process can remove it."""
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except Exception:
            # Non-fatal; lock cleanup best-effort.
            pass

    @contextmanager
    def edit_lock(self, timeout_seconds: float = 30.0) -> Iterator[None]:
        """Context manager for exclusive workbook edit lock."""
        self.acquire_lock(timeout_seconds=timeout_seconds)
        try:
            yield
        finally:
            self.release_lock()

    def _append_manifest(self, record: Dict) -> None:
        """Append a record to history manifest."""
        self.ensure_dirs()
        with open(self.manifest_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True))
            fh.write("\n")

    def _iter_manifest(self) -> Iterator[Dict]:
        """Iterate all manifest records in file order."""
        if not self.manifest_path.exists():
            return
        with open(self.manifest_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue

    def list_snapshots(self, limit: int = 50) -> List[Dict]:
        """Return snapshot records ordered newest-first."""
        records = []
        for record in self._iter_manifest() or []:
            if record.get("record_type") == "snapshot":
                records.append(record)
        records.reverse()
        return records[: max(limit, 1)]

    def get_snapshot(self, revision_id: str) -> Optional[Dict]:
        """Return a snapshot record by revision ID."""
        for record in self._iter_manifest() or []:
            if record.get("record_type") == "snapshot" and record.get("revision_id") == revision_id:
                return record
        return None

    def _find_open_excel_book(self) -> Optional[Tuple[object, object]]:
        """Try to find an open Excel workbook matching target file using xlwings."""
        try:
            import xlwings as xw
        except Exception:
            return None

        target = _normalized_path(self.xlsform_path)
        try:
            for app in xw.apps:
                for book in app.books:
                    full_name = getattr(book, "fullname", None)
                    if not full_name:
                        continue
                    try:
                        candidate = _normalized_path(Path(full_name))
                    except Exception:
                        continue
                    if candidate == target:
                        return app, book
        except Exception:
            return None
        return None

    def _copy_live_workbook_snapshot(self, destination: Path) -> str:
        """Create snapshot from current workbook state."""
        open_book = self._find_open_excel_book()
        if open_book:
            _, book = open_book
            book.api.SaveCopyAs(str(destination))
            return "excel_savecopyas"

        shutil.copy2(self.xlsform_path, destination)
        return "copy2"

    def create_snapshot(
        self,
        action_type: str,
        description: str,
        details: str = "",
        command: str = "",
        agent: str = "",
    ) -> Dict:
        """Create immutable snapshot and append manifest record."""
        if not self.xlsform_path.exists():
            raise FileNotFoundError(f"XLSForm file not found: {self.xlsform_path}")

        self.ensure_dirs()
        revision_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        snapshot_name = f"{revision_id}__{self.xlsform_path.name}"
        snapshot_path = self.snapshots_dir / snapshot_name

        source_hash = _file_sha256(self.xlsform_path)
        method = self._copy_live_workbook_snapshot(snapshot_path)
        snapshot_hash = _file_sha256(snapshot_path)

        record = {
            "record_type": "snapshot",
            "timestamp": _utc_now_iso(),
            "revision_id": revision_id,
            "action_type": action_type,
            "description": description,
            "details": details,
            "command": command,
            "agent": agent,
            "workbook": str(self.xlsform_path.relative_to(self.project_dir))
            if self.xlsform_path.is_relative_to(self.project_dir)
            else str(self.xlsform_path),
            "snapshot_path": str(snapshot_path.relative_to(self.project_dir))
            if snapshot_path.is_relative_to(self.project_dir)
            else str(snapshot_path),
            "source_sha256": source_hash,
            "snapshot_sha256": snapshot_hash,
            "method": method,
        }
        self._append_manifest(record)
        return record

    def append_event(self, action_type: str, description: str, details: str = "", extra: Optional[Dict] = None) -> Dict:
        """Append a non-snapshot event to manifest."""
        record = {
            "record_type": "event",
            "timestamp": _utc_now_iso(),
            "action_type": action_type,
            "description": description,
            "details": details,
            "workbook": str(self.xlsform_path.relative_to(self.project_dir))
            if self.xlsform_path.is_relative_to(self.project_dir)
            else str(self.xlsform_path),
        }
        if extra:
            record.update(extra)
        self._append_manifest(record)
        return record

    def get_latest_snapshot(self, include_pre_restore: bool = False) -> Optional[Dict]:
        """Return most recent snapshot record."""
        for record in self.list_snapshots(limit=500):
            if include_pre_restore:
                return record
            if record.get("action_type") == "pre_restore":
                continue
            return record
        return None

    def restore_snapshot(self, revision_id: str, create_pre_restore_snapshot: bool = True) -> Dict:
        """Restore workbook from a snapshot revision."""
        snapshot_record = self.get_snapshot(revision_id)
        if not snapshot_record:
            raise ValueError(f"Revision not found: {revision_id}")

        snapshot_path = self.project_dir / snapshot_record["snapshot_path"]
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot file missing: {snapshot_path}")

        pre_restore = None
        if create_pre_restore_snapshot and self.xlsform_path.exists():
            pre_restore = self.create_snapshot(
                action_type="pre_restore",
                description=f"Pre-restore safety snapshot before restoring {revision_id}",
                details=f"Target revision: {revision_id}",
                command="/xlsform-revert",
            )

        method = "copy2"
        open_book = self._find_open_excel_book()
        if open_book:
            app, book = open_book
            book.api.Close(False)
            shutil.copy2(snapshot_path, self.xlsform_path)
            app.books.open(str(self.xlsform_path))
            method = "close_copy_reopen"
        else:
            shutil.copy2(snapshot_path, self.xlsform_path)

        restored_hash = _file_sha256(self.xlsform_path)
        event = self.append_event(
            action_type="restore",
            description=f"Restored workbook from revision {revision_id}",
            details=f"Snapshot: {snapshot_record.get('snapshot_path')}",
            extra={
                "restored_from_revision": revision_id,
                "restored_sha256": restored_hash,
                "method": method,
                "pre_restore_revision": pre_restore.get("revision_id") if pre_restore else "",
            },
        )
        return {
            "restored_from": snapshot_record,
            "restore_event": event,
            "pre_restore_snapshot": pre_restore,
        }
