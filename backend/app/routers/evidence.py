"""Evidence router — Module D: evidence and compliance status management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EvidenceCreate, EvidenceOut, ComplianceStatusCreate, ComplianceStatusOut
from app.services.ledger import (
    attach_evidence, update_compliance_status,
    get_evidence_for_obligation, get_status_history,
)

router = APIRouter(prefix="/api/evidence", tags=["Evidence & Compliance"])


@router.post("/{obligation_id}/attach", response_model=EvidenceOut)
def add_evidence(obligation_id: int, evidence: EvidenceCreate, db: Session = Depends(get_db)):
    """Attach evidence to an obligation."""
    return attach_evidence(
        obligation_id=obligation_id,
        evidence_type=evidence.evidence_type,
        title=evidence.title,
        content=evidence.content,
        uploaded_by=evidence.uploaded_by,
        db=db,
    )


@router.get("/{obligation_id}", response_model=list[EvidenceOut])
def list_evidence(obligation_id: int, db: Session = Depends(get_db)):
    """List all evidence for an obligation."""
    return get_evidence_for_obligation(obligation_id, db)


@router.post("/{obligation_id}/status", response_model=ComplianceStatusOut)
def set_compliance_status(obligation_id: int, status: ComplianceStatusCreate, db: Session = Depends(get_db)):
    """Set compliance status (append-only — creates new record, never updates)."""
    return update_compliance_status(
        obligation_id=obligation_id,
        status=status.status,
        changed_by=status.changed_by,
        db=db,
        notes=status.notes,
    )


@router.get("/{obligation_id}/status-history", response_model=list[ComplianceStatusOut])
def get_compliance_history(obligation_id: int, db: Session = Depends(get_db)):
    """Get full compliance status history (audit trail)."""
    return get_status_history(obligation_id, db)
