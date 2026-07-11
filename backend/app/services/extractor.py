"""Module B — LLM-based obligation extraction from clause chunks."""
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.llm.client import generate_json
from app.llm.prompts import OBLIGATION_EXTRACTION_SYSTEM, OBLIGATION_EXTRACTION_PROMPT
from app.models.obligation import Obligation
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def extract_obligations_from_chunk(chunk: dict) -> list[dict]:
    """
    Send a single clause chunk to the LLM and extract structured obligations.
    Returns a list of obligation dicts matching the schema.
    """
    prompt = OBLIGATION_EXTRACTION_PROMPT.format(
        source_document=chunk.get("source_document", "SEBI Master Circular for Stock Brokers"),
        chapter=chunk.get("chapter", "Unknown"),
        section_id=chunk.get("section_id", "0"),
        clause_text=chunk.get("text", ""),
        section_prefix=chunk.get("section_id", "0").replace(".", "-"),
        index=1,
    )

    try:
        result = await generate_json(prompt, system_instruction=OBLIGATION_EXTRACTION_SYSTEM)
        if isinstance(result, dict):
            result = [result]
        if not isinstance(result, list):
            logger.warning(f"LLM returned non-list for chunk {chunk.get('chunk_id')}: {type(result)}")
            return []
        return result
    except Exception as e:
        logger.error(f"Extraction failed for chunk {chunk.get('chunk_id')}: {e}")
        return []


async def extract_obligations_from_chunks(
    chunks: list[dict],
    circular_id: int,
    db: Session,
) -> list[Obligation]:
    """
    Process multiple chunks, extract obligations, and store in DB with pending_review status.
    """
    all_obligations = []
    global_counter = 0

    for chunk in chunks:
        raw_obligations = await extract_obligations_from_chunk(chunk)

        for raw in raw_obligations:
            global_counter += 1
            # Ensure unique obligation_id
            obl_id = raw.get("obligation_id", f"OBL-{circular_id}-{global_counter:04d}")
            # Check for duplicates
            existing = db.query(Obligation).filter(Obligation.obligation_id == obl_id).first()
            if existing:
                obl_id = f"{obl_id}-{global_counter}"

            obligation = Obligation(
                obligation_id=obl_id,
                source_chunk_id=chunk.get("chunk_id"),
                circular_id=circular_id,
                source_clause_ref=raw.get("source_clause_ref", chunk.get("chapter", "")),
                obligation_text_summary=raw.get("obligation_text_summary", ""),
                applicable_intermediary=raw.get("applicable_intermediary", ["Stockbroker"]),
                obligation_type=raw.get("obligation_type", "systems_process"),
                trigger_condition=raw.get("trigger_condition"),
                frequency=raw.get("frequency", "event-based"),
                deadline_rule=raw.get("deadline_rule"),
                evidence_required=raw.get("evidence_required", []),
                penalty_or_risk_if_noncompliant=raw.get("penalty_or_risk_if_noncompliant"),
                confidence_score=raw.get("confidence_score", 0.5),
                review_status="pending_review",
                status="active",
            )
            db.add(obligation)
            all_obligations.append(obligation)

            # Audit log
            audit = AuditLog(
                entity_type="obligation",
                entity_id=obl_id,
                action="extracted",
                new_value=raw.get("obligation_text_summary", ""),
                user="system",
                timestamp=datetime.utcnow(),
                details=f"Extracted from chunk {chunk.get('chunk_id')} with confidence {raw.get('confidence_score', 0)}",
            )
            db.add(audit)

    db.commit()
    logger.info(f"Extracted and stored {len(all_obligations)} obligations from {len(chunks)} chunks")
    return all_obligations
