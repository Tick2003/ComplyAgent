"""Gap-Finder Agent — scans obligations for compliance gaps and suggests remediation."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.llm.client import generate_json
from app.llm.prompts import GAP_ANALYSIS_PROMPT
from app.models.obligation import Obligation
from app.models.evidence import Evidence, ComplianceStatus

logger = logging.getLogger(__name__)


async def find_gaps(db: Session) -> dict:
    """
    Scan all active obligations and identify compliance gaps:
    - Overdue obligations (non-compliant or no status)
    - Missing evidence
    - Low confidence extractions needing re-review
    """
    active_obligations = db.query(Obligation).filter(
        Obligation.status == "active",
        Obligation.review_status == "approved",
    ).all()

    overdue = []
    missing_evidence = []
    low_confidence = []
    remediation_suggestions = []

    for obl in active_obligations:
        # Get current compliance status (latest row)
        current_status = (
            db.query(ComplianceStatus)
            .filter(ComplianceStatus.obligation_id == obl.id)
            .order_by(desc(ComplianceStatus.changed_at))
            .first()
        )

        # Get evidence count
        evidence_count = db.query(Evidence).filter(Evidence.obligation_id == obl.id).count()

        status_val = current_status.status if current_status else "no_status"

        # Check for overdue (non-compliant status)
        if status_val in ("non_compliant", "no_status"):
            gap_info = {
                "obligation_id": obl.obligation_id,
                "db_id": obl.id,
                "summary": obl.obligation_text_summary,
                "obligation_type": obl.obligation_type,
                "deadline_rule": obl.deadline_rule,
                "current_status": status_val,
                "evidence_count": evidence_count,
            }
            overdue.append(gap_info)

            # Get remediation suggestion
            suggestion = await _get_remediation(obl, status_val, evidence_count, "overdue")
            if suggestion:
                remediation_suggestions.append({**gap_info, **suggestion})

        # Check for missing evidence
        if evidence_count == 0 and status_val != "not_yet_due":
            gap_info = {
                "obligation_id": obl.obligation_id,
                "db_id": obl.id,
                "summary": obl.obligation_text_summary,
                "obligation_type": obl.obligation_type,
                "current_status": status_val,
                "evidence_required": obl.evidence_required,
            }
            # Avoid duplicates with overdue
            if not any(o["obligation_id"] == obl.obligation_id for o in missing_evidence):
                missing_evidence.append(gap_info)

                if not any(r["obligation_id"] == obl.obligation_id for r in remediation_suggestions):
                    suggestion = await _get_remediation(obl, status_val, evidence_count, "missing_evidence")
                    if suggestion:
                        remediation_suggestions.append({**gap_info, **suggestion})

        # Check for low confidence
        if obl.confidence_score < 0.6:
            low_confidence.append({
                "obligation_id": obl.obligation_id,
                "db_id": obl.id,
                "summary": obl.obligation_text_summary,
                "confidence_score": obl.confidence_score,
                "source_clause_ref": obl.source_clause_ref,
            })

    total_gaps = len(overdue) + len(missing_evidence) + len(low_confidence)

    # Generate priority summary
    priority_summary = _generate_priority_summary(overdue, missing_evidence, low_confidence)

    return {
        "overdue": overdue,
        "missing_evidence": missing_evidence,
        "low_confidence": low_confidence,
        "total_gaps": total_gaps,
        "priority_summary": priority_summary,
        "remediation_suggestions": remediation_suggestions,
    }


async def _get_remediation(obl: Obligation, status: str, evidence_count: int, gap_type: str) -> dict | None:
    """Get AI-powered remediation suggestion for a gap."""
    try:
        prompt = GAP_ANALYSIS_PROMPT.format(
            obligation_id=obl.obligation_id,
            summary=obl.obligation_text_summary,
            obligation_type=obl.obligation_type,
            deadline_rule=obl.deadline_rule or "Not specified",
            current_status=status,
            evidence_count=evidence_count,
            gap_type=gap_type,
        )
        result = await generate_json(prompt)
        return result
    except Exception as e:
        logger.warning(f"Remediation suggestion failed for {obl.obligation_id}: {e}")
        return {
            "severity": "medium",
            "responsible_team": "Compliance Department",
            "suggested_deadline_days": 15,
            "remediation_steps": ["Review obligation requirements", "Gather necessary evidence", "Update compliance status"],
            "template_evidence": obl.evidence_required or ["compliance documentation"],
            "risk_if_unresolved": obl.penalty_or_risk_if_noncompliant or "Regulatory risk",
        }


def _generate_priority_summary(overdue: list, missing_evidence: list, low_confidence: list) -> str:
    """Generate a plain-English priority summary."""
    parts = []
    if overdue:
        parts.append(f"🚨 {len(overdue)} obligation(s) are overdue or non-compliant and require immediate attention")
    if missing_evidence:
        parts.append(f"⚠️ {len(missing_evidence)} obligation(s) have no evidence attached")
    if low_confidence:
        parts.append(f"🔍 {len(low_confidence)} obligation(s) have low extraction confidence and need human re-review")
    if not parts:
        return "✅ No compliance gaps detected. All active obligations are on track."
    return ". ".join(parts) + "."
