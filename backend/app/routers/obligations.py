"""Obligations router — CRUD, review, process mapping."""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.obligation import Obligation, ObligationProcessMap
from app.models.evidence import ComplianceStatus, Evidence
from app.models.audit_log import AuditLog
from app.schemas import (
    ObligationOut, ObligationReview, ObligationUpdate,
    ProcessMapOut, ProcessMapCreate, AuditLogOut,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/obligations", tags=["Obligations"])


@router.get("/", response_model=list[ObligationOut])
def list_obligations(
    status: str = Query(None),
    review_status: str = Query(None),
    obligation_type: str = Query(None),
    process_area: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
):
    """List obligations with filtering."""
    query = db.query(Obligation)

    if status:
        query = query.filter(Obligation.status == status)
    if review_status:
        query = query.filter(Obligation.review_status == review_status)
    if obligation_type:
        query = query.filter(Obligation.obligation_type == obligation_type)
    if search:
        query = query.filter(Obligation.obligation_text_summary.ilike(f"%{search}%"))
    if process_area:
        query = query.join(ObligationProcessMap).filter(
            ObligationProcessMap.process_name.ilike(f"%{process_area}%")
        )

    obligations = query.order_by(Obligation.created_at.desc()).all()
    return [_obligation_to_out(o, db) for o in obligations]


@router.get("/{obligation_id}", response_model=ObligationOut)
def get_obligation(obligation_id: int, db: Session = Depends(get_db)):
    """Get a single obligation by DB id."""
    obl = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obl:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return _obligation_to_out(obl, db)


@router.put("/{obligation_id}/review")
def review_obligation(obligation_id: int, review: ObligationReview, db: Session = Depends(get_db)):
    """Approve or reject an extracted obligation (human-in-the-loop)."""
    obl = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obl:
        raise HTTPException(status_code=404, detail="Obligation not found")

    old_status = obl.review_status
    obl.review_status = review.review_status
    obl.reviewed_by = review.reviewed_by
    obl.reviewed_at = datetime.utcnow()
    obl.review_notes = review.review_notes

    audit = AuditLog(
        entity_type="obligation",
        entity_id=obl.obligation_id,
        action="reviewed",
        old_value=old_status,
        new_value=review.review_status,
        user=review.reviewed_by,
        timestamp=datetime.utcnow(),
        details=review.review_notes,
    )
    db.add(audit)
    db.commit()
    db.refresh(obl)
    return _obligation_to_out(obl, db)


@router.put("/{obligation_id}")
def update_obligation(obligation_id: int, update: ObligationUpdate, db: Session = Depends(get_db)):
    """Update an obligation's fields (human edit)."""
    obl = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obl:
        raise HTTPException(status_code=404, detail="Obligation not found")

    changes = {}
    for field, value in update.model_dump(exclude_none=True).items():
        old_val = getattr(obl, field)
        setattr(obl, field, value)
        changes[field] = {"old": str(old_val), "new": str(value)}

    if changes:
        import json
        audit = AuditLog(
            entity_type="obligation",
            entity_id=obl.obligation_id,
            action="updated",
            old_value=json.dumps({k: v["old"] for k, v in changes.items()}),
            new_value=json.dumps({k: v["new"] for k, v in changes.items()}),
            user="compliance_officer",
            timestamp=datetime.utcnow(),
        )
        db.add(audit)

    db.commit()
    db.refresh(obl)
    return _obligation_to_out(obl, db)


@router.get("/{obligation_id}/processes", response_model=list[ProcessMapOut])
def get_process_mappings(obligation_id: int, db: Session = Depends(get_db)):
    """Get process mappings for an obligation."""
    maps = db.query(ObligationProcessMap).filter(
        ObligationProcessMap.obligation_id == obligation_id
    ).all()
    return maps


@router.post("/{obligation_id}/processes", response_model=ProcessMapOut)
def add_process_mapping(obligation_id: int, mapping: ProcessMapCreate, db: Session = Depends(get_db)):
    """Add a manual process mapping override."""
    from app.services.mapper import override_process_mapping
    return override_process_mapping(obligation_id, mapping.process_name, "compliance_officer", db)


@router.get("/{obligation_id}/audit-trail", response_model=list[AuditLogOut])
def get_obligation_audit_trail(obligation_id: int, db: Session = Depends(get_db)):
    """Get full audit trail for an obligation."""
    obl = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obl:
        raise HTTPException(status_code=404, detail="Obligation not found")
    logs = db.query(AuditLog).filter(
        AuditLog.entity_id == obl.obligation_id
    ).order_by(desc(AuditLog.timestamp)).all()
    return logs


def _obligation_to_out(obl: Obligation, db: Session) -> ObligationOut:
    """Convert Obligation model to output schema with computed fields."""
    # Current compliance status
    current_status = (
        db.query(ComplianceStatus)
        .filter(ComplianceStatus.obligation_id == obl.id)
        .order_by(desc(ComplianceStatus.changed_at))
        .first()
    )

    # Process areas
    process_maps = db.query(ObligationProcessMap).filter(
        ObligationProcessMap.obligation_id == obl.id
    ).all()

    # Evidence count
    evidence_count = db.query(Evidence).filter(Evidence.obligation_id == obl.id).count()

    return ObligationOut(
        id=obl.id,
        obligation_id=obl.obligation_id,
        source_chunk_id=obl.source_chunk_id,
        circular_id=obl.circular_id,
        source_clause_ref=obl.source_clause_ref,
        obligation_text_summary=obl.obligation_text_summary,
        applicable_intermediary=obl.applicable_intermediary or ["Stockbroker"],
        obligation_type=obl.obligation_type,
        trigger_condition=obl.trigger_condition,
        frequency=obl.frequency,
        deadline_rule=obl.deadline_rule,
        evidence_required=obl.evidence_required,
        penalty_or_risk_if_noncompliant=obl.penalty_or_risk_if_noncompliant,
        confidence_score=obl.confidence_score,
        review_status=obl.review_status,
        status=obl.status,
        created_at=obl.created_at,
        current_compliance_status=current_status.status if current_status else None,
        process_areas=[pm.process_name for pm in process_maps],
        evidence_count=evidence_count,
    )
