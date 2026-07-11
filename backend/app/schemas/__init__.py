"""Pydantic schemas for API request/response validation."""
from datetime import datetime, date
from pydantic import BaseModel, Field


# ── Circular Schemas ──────────────────────────────────────────────────
class CircularCreate(BaseModel):
    title: str
    circular_number: str | None = None
    source_url: str | None = None
    effective_date: date | None = None
    circular_type: str = "master_circular"

class CircularOut(BaseModel):
    id: int
    title: str
    circular_number: str | None
    source_url: str | None
    effective_date: date | None
    upload_date: datetime
    status: str
    circular_type: str
    summary: str | None
    chunk_count: int = 0
    obligation_count: int = 0
    model_config = {"from_attributes": True}

class ClauseChunkOut(BaseModel):
    id: int
    chunk_id: str
    chapter: str | None
    section_id: str | None
    page_number: int | None
    text: str
    effective_date: date | None
    model_config = {"from_attributes": True}


# ── Obligation Schemas ────────────────────────────────────────────────
class ObligationExtracted(BaseModel):
    """Schema for LLM-extracted obligation — matches the build brief exactly."""
    obligation_id: str
    source_clause_ref: str
    obligation_text_summary: str
    applicable_intermediary: list[str] = ["Stockbroker"]
    obligation_type: str
    trigger_condition: str | None = None
    frequency: str = "event-based"
    deadline_rule: str | None = None
    evidence_required: list[str] = []
    penalty_or_risk_if_noncompliant: str | None = None
    confidence_score: float = 0.0

class ObligationOut(BaseModel):
    id: int
    obligation_id: str
    source_chunk_id: str | None
    circular_id: int | None
    source_clause_ref: str | None
    obligation_text_summary: str
    applicable_intermediary: list[str]
    obligation_type: str
    trigger_condition: str | None
    frequency: str
    deadline_rule: str | None
    evidence_required: list[str] | None
    penalty_or_risk_if_noncompliant: str | None
    confidence_score: float
    review_status: str
    status: str
    created_at: datetime
    # Computed fields
    current_compliance_status: str | None = None
    process_areas: list[str] = []
    evidence_count: int = 0
    model_config = {"from_attributes": True}

class ObligationReview(BaseModel):
    review_status: str = Field(..., pattern="^(approved|rejected)$")
    reviewed_by: str
    review_notes: str | None = None

class ObligationUpdate(BaseModel):
    obligation_text_summary: str | None = None
    obligation_type: str | None = None
    trigger_condition: str | None = None
    frequency: str | None = None
    deadline_rule: str | None = None
    evidence_required: list[str] | None = None
    penalty_or_risk_if_noncompliant: str | None = None


# ── Process Mapping Schemas ───────────────────────────────────────────
class ProcessMapOut(BaseModel):
    id: int
    process_name: str
    confidence: float
    is_override: bool
    model_config = {"from_attributes": True}

class ProcessMapCreate(BaseModel):
    process_name: str
    is_override: bool = True


# ── Evidence Schemas ──────────────────────────────────────────────────
class EvidenceCreate(BaseModel):
    evidence_type: str = Field(..., pattern="^(document|link|checkbox|data_feed)$")
    title: str
    content: str | None = None
    uploaded_by: str

class EvidenceOut(BaseModel):
    id: int
    obligation_id: int
    evidence_type: str
    title: str
    content: str | None
    file_path: str | None
    uploaded_by: str
    uploaded_at: datetime
    model_config = {"from_attributes": True}


# ── Compliance Status Schemas ─────────────────────────────────────────
class ComplianceStatusCreate(BaseModel):
    status: str = Field(..., pattern="^(compliant|partially_compliant|non_compliant|not_yet_due)$")
    changed_by: str
    notes: str | None = None

class ComplianceStatusOut(BaseModel):
    id: int
    obligation_id: int
    status: str
    changed_by: str
    changed_at: datetime
    notes: str | None
    model_config = {"from_attributes": True}


# ── Audit Log Schemas ─────────────────────────────────────────────────
class AuditLogOut(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    action: str
    old_value: str | None
    new_value: str | None
    user: str
    timestamp: datetime
    details: str | None
    model_config = {"from_attributes": True}


# ── Dashboard Schemas ─────────────────────────────────────────────────
class DashboardStats(BaseModel):
    health_score: float
    total_obligations: int
    compliant: int
    partially_compliant: int
    non_compliant: int
    not_yet_due: int
    pending_review: int
    overdue_count: int
    missing_evidence_count: int
    obligations_by_type: dict[str, int]
    obligations_by_process: dict[str, int]
    upcoming_deadlines: list[dict]
    recent_changes: list[dict]


# ── Agent Schemas ─────────────────────────────────────────────────────
class ChangeDetectionResult(BaseModel):
    new_obligations: list[dict]
    modified_obligations: list[dict]
    superseded_obligations: list[dict]
    summary: str

class GapReport(BaseModel):
    overdue: list[dict]
    missing_evidence: list[dict]
    low_confidence: list[dict]
    total_gaps: int
    priority_summary: str
    remediation_suggestions: list[dict]

class QueryRequest(BaseModel):
    question: str
    user: str = "compliance_officer"

class QueryResponse(BaseModel):
    answer: str
    citations: list[dict]
    related_obligations: list[dict]
    confidence: float
