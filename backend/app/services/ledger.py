"""Module D — Evidence ledger and compliance status tracking with append-only audit trail."""
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.evidence import Evidence, ComplianceStatus
from app.models.obligation import Obligation
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def attach_evidence(
    obligation_id: int,
    evidence_type: str,
    title: str,
    content: str | None,
    uploaded_by: str,
    db: Session,
    file_path: str | None = None,
) -> Evidence:
    """Attach evidence to an obligation. Creates audit log entry."""
    evidence = Evidence(
        obligation_id=obligation_id,
        evidence_type=evidence_type,
        title=title,
        content=content,
        file_path=file_path,
        uploaded_by=uploaded_by,
    )
    db.add(evidence)

    audit = AuditLog(
        entity_type="evidence",
        entity_id=str(evidence.id) if evidence.id else "new",
        action="evidence_attached",
        new_value=json.dumps({"type": evidence_type, "title": title}),
        user=uploaded_by,
        timestamp=datetime.utcnow(),
        details=f"Evidence attached to obligation {obligation_id}",
    )
    db.add(audit)
    db.commit()
    db.refresh(evidence)

    # Also audit on the obligation
    obl_audit = AuditLog(
        entity_type="obligation",
        entity_id=str(obligation_id),
        action="evidence_attached",
        new_value=title,
        user=uploaded_by,
        timestamp=datetime.utcnow(),
    )
    db.add(obl_audit)
    db.commit()

    return evidence


def update_compliance_status(
    obligation_id: int,
    status: str,
    changed_by: str,
    db: Session,
    notes: str | None = None,
) -> ComplianceStatus:
    """
    Append a new compliance status record (never update/delete existing).
    Current status = latest row for this obligation_id.
    """
    # Get current status for audit diff
    current = get_current_status(obligation_id, db)
    old_status = current.status if current else "none"

    new_status = ComplianceStatus(
        obligation_id=obligation_id,
        status=status,
        changed_by=changed_by,
        changed_at=datetime.utcnow(),
        notes=notes,
    )
    db.add(new_status)

    audit = AuditLog(
        entity_type="compliance_status",
        entity_id=str(obligation_id),
        action="status_changed",
        old_value=old_status,
        new_value=status,
        user=changed_by,
        timestamp=datetime.utcnow(),
        details=notes,
    )
    db.add(audit)
    db.commit()
    db.refresh(new_status)

    logger.info(f"Obligation {obligation_id} status: {old_status} → {status} by {changed_by}")
    return new_status


def get_current_status(obligation_id: int, db: Session) -> ComplianceStatus | None:
    """Get the most recent compliance status for an obligation."""
    return (
        db.query(ComplianceStatus)
        .filter(ComplianceStatus.obligation_id == obligation_id)
        .order_by(desc(ComplianceStatus.changed_at))
        .first()
    )


def get_status_history(obligation_id: int, db: Session) -> list[ComplianceStatus]:
    """Get the full status history (audit trail) for an obligation."""
    return (
        db.query(ComplianceStatus)
        .filter(ComplianceStatus.obligation_id == obligation_id)
        .order_by(desc(ComplianceStatus.changed_at))
        .all()
    )


def get_evidence_for_obligation(obligation_id: int, db: Session) -> list[Evidence]:
    """Get all evidence items attached to an obligation."""
    return (
        db.query(Evidence)
        .filter(Evidence.obligation_id == obligation_id)
        .order_by(desc(Evidence.uploaded_at))
        .all()
    )


def get_audit_trail(entity_type: str | None, entity_id: str | None, db: Session, limit: int = 100) -> list[AuditLog]:
    """Get audit trail, optionally filtered by entity."""
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    return query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
