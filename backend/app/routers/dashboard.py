"""Dashboard router — Module F: aggregated stats and health score."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from collections import Counter

from app.database import get_db
from app.schemas import DashboardStats
from app.models.obligation import Obligation, ObligationProcessMap
from app.models.evidence import ComplianceStatus, Evidence
from app.models.audit_log import AuditLog
from app.models.circular import Circular

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get aggregated dashboard statistics and health score."""

    # Get all active, approved obligations
    obligations = db.query(Obligation).filter(
        Obligation.status == "active",
    ).all()

    total = len(obligations)
    pending_review = sum(1 for o in obligations if o.review_status == "pending_review")

    # Count by compliance status
    status_counts = Counter()
    overdue_count = 0
    missing_evidence_count = 0
    upcoming_deadlines = []

    for obl in obligations:
        # Current status
        current = (
            db.query(ComplianceStatus)
            .filter(ComplianceStatus.obligation_id == obl.id)
            .order_by(desc(ComplianceStatus.changed_at))
            .first()
        )
        status_val = current.status if current else "not_yet_due"
        status_counts[status_val] += 1

        if status_val == "non_compliant":
            overdue_count += 1

        # Evidence check
        evidence_count = db.query(Evidence).filter(Evidence.obligation_id == obl.id).count()
        if evidence_count == 0 and obl.review_status == "approved":
            missing_evidence_count += 1

        # Deadlines
        if obl.deadline_rule and obl.review_status == "approved":
            upcoming_deadlines.append({
                "obligation_id": obl.obligation_id,
                "summary": obl.obligation_text_summary[:100],
                "deadline_rule": obl.deadline_rule,
                "status": status_val,
                "type": obl.obligation_type,
            })

    # Calculate health score
    approved_obligations = [o for o in obligations if o.review_status == "approved"]
    if approved_obligations:
        score_map = {"compliant": 100, "partially_compliant": 50, "non_compliant": 0, "not_yet_due": 75}
        scores = []
        for obl in approved_obligations:
            current = (
                db.query(ComplianceStatus)
                .filter(ComplianceStatus.obligation_id == obl.id)
                .order_by(desc(ComplianceStatus.changed_at))
                .first()
            )
            status_val = current.status if current else "not_yet_due"
            scores.append(score_map.get(status_val, 50))
        health_score = sum(scores) / len(scores)
    else:
        health_score = 100.0

    # Obligations by type
    type_counts = Counter(o.obligation_type for o in obligations)

    # Obligations by process
    process_counts = Counter()
    for obl in obligations:
        maps = db.query(ObligationProcessMap).filter(
            ObligationProcessMap.obligation_id == obl.id
        ).all()
        for m in maps:
            process_counts[m.process_name] += 1

    # Recent changes (last 10 audit log entries)
    recent_logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(10).all()
    recent_changes = [
        {
            "id": log.id,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "action": log.action,
            "user": log.user,
            "timestamp": log.timestamp.isoformat(),
            "details": log.details,
        }
        for log in recent_logs
    ]

    return DashboardStats(
        health_score=round(health_score, 1),
        total_obligations=total,
        compliant=status_counts.get("compliant", 0),
        partially_compliant=status_counts.get("partially_compliant", 0),
        non_compliant=status_counts.get("non_compliant", 0),
        not_yet_due=status_counts.get("not_yet_due", 0),
        pending_review=pending_review,
        overdue_count=overdue_count,
        missing_evidence_count=missing_evidence_count,
        obligations_by_type=dict(type_counts),
        obligations_by_process=dict(process_counts),
        upcoming_deadlines=upcoming_deadlines[:10],
        recent_changes=recent_changes,
    )
