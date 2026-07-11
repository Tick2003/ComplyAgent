"""Universal audit log — append-only, never delete. Blockchain-inspired hash chain."""
import hashlib
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditLog(Base):
    """
    Immutable audit trail with cryptographic hash chain.
    Each entry contains a SHA-256 hash linking it to the previous entry,
    creating a tamper-evident, blockchain-inspired compliance record.
    """
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    action: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    user: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    details: Mapped[str | None] = mapped_column(Text)
    # Hash chain fields — blockchain-inspired immutability
    prev_hash: Mapped[str | None] = mapped_column(String(64), default="0" * 64)
    entry_hash: Mapped[str | None] = mapped_column(String(64), index=True)

    @staticmethod
    def compute_hash(entity_type: str, entity_id: str, action: str,
                     timestamp: str, user: str, prev_hash: str) -> str:
        """Compute SHA-256 hash for this audit entry, chained to previous."""
        payload = f"{prev_hash}|{entity_type}|{entity_id}|{action}|{timestamp}|{user}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

