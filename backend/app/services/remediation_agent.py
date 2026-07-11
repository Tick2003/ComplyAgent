"""Remediation Agent — suggests concrete next steps for compliance gaps."""
import logging
from app.llm.client import generate_json
from app.models.obligation import Obligation

logger = logging.getLogger(__name__)


async def suggest_remediation(obligation: Obligation, gap_type: str, current_status: str, evidence_count: int) -> dict:
    """Generate remediation suggestions for a specific compliance gap."""
    prompt = f"""You are a compliance remediation advisor for SEBI-regulated stockbrokers.

An obligation has a compliance gap that needs remediation:

OBLIGATION DETAILS:
- ID: {obligation.obligation_id}
- Summary: {obligation.obligation_text_summary}
- Type: {obligation.obligation_type}
- Deadline Rule: {obligation.deadline_rule or 'Not specified'}
- Frequency: {obligation.frequency}
- Current Status: {current_status}
- Evidence Items: {evidence_count}
- Gap Type: {gap_type}
- Required Evidence: {obligation.evidence_required}

Provide remediation guidance as JSON:
{{
    "severity": "critical | high | medium | low",
    "responsible_team": "which team/process owner should handle this",
    "suggested_deadline_days": number,
    "remediation_steps": ["step 1", "step 2", "step 3"],
    "template_evidence": ["specific evidence/documents needed"],
    "risk_if_unresolved": "what happens if this isn't fixed",
    "estimated_effort": "hours or days estimate",
    "priority_rank": 1-10
}}"""

    try:
        result = await generate_json(prompt)
        return result
    except Exception as e:
        logger.warning(f"Remediation suggestion LLM call failed: {e}")
        # Provide sensible defaults
        return {
            "severity": "medium",
            "responsible_team": "Compliance Department",
            "suggested_deadline_days": 15,
            "remediation_steps": [
                "Review the obligation requirements",
                "Identify responsible stakeholders",
                "Gather and attach required evidence",
                "Update the compliance status",
            ],
            "template_evidence": obligation.evidence_required or ["Compliance documentation"],
            "risk_if_unresolved": obligation.penalty_or_risk_if_noncompliant or "Potential regulatory action by SEBI",
            "estimated_effort": "2-4 hours",
            "priority_rank": 5,
        }
