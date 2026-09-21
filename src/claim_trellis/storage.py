from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from claim_trellis.models import AuditEvent, ClaimAudit, HumanReview


class AuditStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS audits (
                    audit_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    record_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    audit_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY (audit_id) REFERENCES audits(audit_id)
                );
                CREATE INDEX IF NOT EXISTS idx_audit_events_audit_id
                ON audit_events(audit_id, created_at);
                """
            )

    def save(self, audit: ClaimAudit, *, event_type: str = "audit.created") -> ClaimAudit:
        now = datetime.now(UTC).isoformat()
        record = audit.model_dump_json()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audits (audit_id, created_at, updated_at, record_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(audit_id) DO UPDATE SET updated_at=excluded.updated_at, record_json=excluded.record_json
                """,
                (audit.audit_id, audit.provenance.created_at.isoformat(), now, record),
            )
            self._append_event(
                connection, audit.audit_id, event_type, audit.model_dump(mode="json")
            )
        return audit

    def _append_event(
        self,
        connection: sqlite3.Connection,
        audit_id: str,
        event_type: str,
        payload: dict[str, object],
    ) -> None:
        connection.execute(
            "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?)",
            (
                str(uuid4()),
                audit_id,
                event_type,
                datetime.now(UTC).isoformat(),
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            ),
        )

    def get(self, audit_id: str) -> ClaimAudit | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM audits WHERE audit_id = ?", (audit_id,)
            ).fetchone()
        return ClaimAudit.model_validate_json(row["record_json"]) if row else None

    def list_audits(self, *, limit: int = 50) -> list[ClaimAudit]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM audits ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [ClaimAudit.model_validate_json(row["record_json"]) for row in rows]

    def add_review(self, audit_id: str, review: HumanReview) -> ClaimAudit | None:
        audit = self.get(audit_id)
        if audit is None:
            return None
        updated = audit.model_copy(update={"human_review": review})
        return self.save(updated, event_type="review.recorded")

    def events(self, audit_id: str) -> list[AuditEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_events WHERE audit_id = ? ORDER BY created_at", (audit_id,)
            ).fetchall()
        return [
            AuditEvent(
                event_id=row["event_id"],
                audit_id=row["audit_id"],
                event_type=row["event_type"],
                created_at=datetime.fromisoformat(row["created_at"]),
                payload=json.loads(row["payload_json"]),
            )
            for row in rows
        ]
