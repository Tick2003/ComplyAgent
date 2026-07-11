"""Change Detection Agent — diffs new circulars against existing obligations."""
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.llm.client import generate_json, generate_text
from app.llm.prompts import CHANGE_DETECTION_PROMPT
from app.models.obligation import Obligation
from app.models.audit_log import AuditLog
from app.vector_store.store import query_store

logger = logging.getLogger(__name__)


async def detect_changes(
    new_chunks: list[dict],
    db: Session,
) -> dict:
    """
    Compare new circular chunks against existing obligations.
    Returns a structured change report.
    """
    new_obligations = []
    modified_obligations = []
    superseded_obligations = []

    for chunk in new_chunks:
        text = chunk.get("text", "")
        if not text.strip():
            continue

        # Find semantically similar existing obligations via vector store
        similar = query_store(text, n_results=3)

        if not similar or all(s.get("relevance_score", 0) < 0.3 for s in similar):
            # No match found — this is likely a new obligation
            new_obligations.append({
                "chunk": chunk,
                "change_type": "new",
                "what_changed": "New regulatory requirement not present in existing obligations.",
                "operational_impact": "New compliance obligation needs to be assessed and implemented.",
                "urgency": "high",
            })
            continue

        # Find the most relevant existing obligation
        best_match = similar[0]
        best_match_chunk_id = best_match.get("chunk_id", "")

        # Find the obligation linked to this chunk
        existing_obl = db.query(Obligation).filter(
            Obligation.source_chunk_id == best_match_chunk_id,
            Obligation.status == "active",
        ).first()

        if not existing_obl:
            # Chunk exists but no active obligation — treat as new
            new_obligations.append({
                "chunk": chunk,
                "change_type": "new",
                "what_changed": "Related clause exists but no active obligation was linked.",
                "operational_impact": "Review and create obligation if applicable.",
                "urgency": "medium",
            })
            continue

        # Use LLM to analyze the specific change
        try:
            prompt = CHANGE_DETECTION_PROMPT.format(
                existing_id=existing_obl.obligation_id,
                existing_summary=existing_obl.obligation_text_summary,
                existing_deadline=existing_obl.deadline_rule or "None specified",
                existing_source=existing_obl.source_clause_ref or "",
                new_clause_text=text,
            )
            analysis = await generate_json(prompt)

            change_type = analysis.get("change_type", "unchanged")
            if change_type == "modified":
                modified_obligations.append({
                    "existing_obligation": {
                        "id": existing_obl.id,
                        "obligation_id": existing_obl.obligation_id,
                        "summary": existing_obl.obligation_text_summary,
                        "deadline_rule": existing_obl.deadline_rule,
                    },
                    "new_clause_text": text,
                    "what_changed": analysis.get("what_changed", ""),
                    "operational_impact": analysis.get("operational_impact", ""),
                    "urgency": analysis.get("urgency", "medium"),
                    "suggested_action": analysis.get("suggested_action", ""),
                })

                # Log the change
                audit = AuditLog(
                    entity_type="obligation",
                    entity_id=existing_obl.obligation_id,
                    action="change_detected",
                    old_value=existing_obl.obligation_text_summary,
                    new_value=analysis.get("what_changed", ""),
                    user="change_detection_agent",
                    timestamp=datetime.utcnow(),
                    details=analysis.get("operational_impact", ""),
                )
                db.add(audit)

            elif change_type == "superseded":
                superseded_obligations.append({
                    "existing_obligation": {
                        "id": existing_obl.id,
                        "obligation_id": existing_obl.obligation_id,
                        "summary": existing_obl.obligation_text_summary,
                    },
                    "what_changed": analysis.get("what_changed", ""),
                    "suggested_action": analysis.get("suggested_action", ""),
                })

        except Exception as e:
            logger.error(f"Change analysis failed: {e}")

    db.commit()

    # Generate overall summary
    summary = await _generate_change_summary(new_obligations, modified_obligations, superseded_obligations)

    return {
        "new_obligations": new_obligations,
        "modified_obligations": modified_obligations,
        "superseded_obligations": superseded_obligations,
        "summary": summary,
    }


async def _generate_change_summary(new: list, modified: list, superseded: list) -> str:
    """Generate a plain-English summary of all changes."""
    if not new and not modified and not superseded:
        return "No significant regulatory changes detected."

    prompt = f"""Summarize the following regulatory changes in plain English for a compliance officer:
- {len(new)} new obligations detected
- {len(modified)} existing obligations modified
- {len(superseded)} obligations potentially superseded

Modified obligations details:
{chr(10).join(f"- {m.get('what_changed', '')} (Urgency: {m.get('urgency', 'medium')})" for m in modified)}

Write a concise 2-3 paragraph executive summary highlighting the most important changes and recommended actions."""

    try:
        return await generate_text(prompt)
    except Exception:
        parts = []
        if new:
            parts.append(f"{len(new)} new obligations identified")
        if modified:
            parts.append(f"{len(modified)} existing obligations modified")
        if superseded:
            parts.append(f"{len(superseded)} obligations potentially superseded")
        return "Regulatory changes detected: " + "; ".join(parts) + ". Please review the detailed change report."
