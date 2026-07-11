"""Hash-chain integrity service — verifies tamper-proof audit trail."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

GENESIS_HASH = "0" * 64


def create_chained_audit_entry(
    db: Session,
    entity_type: str,
    entity_id: str,
    action: str,
    user: str,
    old_value: str | None = None,
    new_value: str | None = None,
    details: str | None = None,
) -> AuditLog:
    """Create a new audit log entry with hash chain linking."""
    # Get previous entry's hash
    prev_entry = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = prev_entry.entry_hash if prev_entry and prev_entry.entry_hash else GENESIS_HASH

    from datetime import datetime
    ts = datetime.utcnow()

    entry_hash = AuditLog.compute_hash(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        timestamp=ts.isoformat(),
        user=user,
        prev_hash=prev_hash,
    )

    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        user=user,
        timestamp=ts,
        details=details,
        prev_hash=prev_hash,
        entry_hash=entry_hash,
    )
    db.add(entry)
    return entry


def verify_chain_integrity(db: Session) -> dict:
    """
    Verify the entire audit trail hash chain.
    Returns verification result with any broken links identified.
    """
    entries = db.query(AuditLog).order_by(asc(AuditLog.id)).all()

    if not entries:
        return {
            "verified": True,
            "total_entries": 0,
            "broken_links": [],
            "message": "No audit entries to verify.",
        }

    broken_links = []
    verified_count = 0
    prev_hash = GENESIS_HASH

    for entry in entries:
        # Skip entries without hash (pre-chain entries)
        if not entry.entry_hash:
            prev_hash = GENESIS_HASH
            verified_count += 1
            continue

        expected_hash = AuditLog.compute_hash(
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            action=entry.action,
            timestamp=entry.timestamp.isoformat(),
            user=entry.user,
            prev_hash=entry.prev_hash or GENESIS_HASH,
        )

        if entry.entry_hash != expected_hash:
            broken_links.append({
                "entry_id": entry.id,
                "entity_type": entry.entity_type,
                "entity_id": entry.entity_id,
                "action": entry.action,
                "timestamp": entry.timestamp.isoformat(),
                "expected_hash": expected_hash[:16] + "...",
                "actual_hash": entry.entry_hash[:16] + "...",
            })
        else:
            verified_count += 1

        prev_hash = entry.entry_hash

    is_verified = len(broken_links) == 0

    return {
        "verified": is_verified,
        "total_entries": len(entries),
        "verified_entries": verified_count,
        "broken_links": broken_links,
        "chain_head_hash": entries[-1].entry_hash[:16] + "..." if entries[-1].entry_hash else None,
        "message": (
            f"Chain integrity VERIFIED. {verified_count} entries validated."
            if is_verified
            else f"INTEGRITY BREACH: {len(broken_links)} broken link(s) detected!"
        ),
    }
