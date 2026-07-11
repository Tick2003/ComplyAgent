"""Module C — Map obligations to stockbroker operational processes."""
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.llm.client import generate_json
from app.llm.prompts import PROCESS_MAPPING_PROMPT
from app.models.obligation import Obligation, ObligationProcessMap
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

# Canonical process taxonomy for stockbrokers
PROCESS_AREAS = [
    "Client Onboarding (KYC/AML)",
    "Trading & Order Management",
    "Margin & Risk Management",
    "Investor Grievance Redressal",
    "Reporting to Exchange/SEBI",
    "Cybersecurity & IT Infrastructure",
    "Advertising & Marketing",
    "Record-Keeping & Documentation",
    "Settlement & Accounts",
    "Audit & Supervision",
]

# Rule-based fallback mapping (obligation_type → process areas)
TYPE_TO_PROCESS = {
    "kyc_onboarding": ["Client Onboarding (KYC/AML)"],
    "reporting": ["Reporting to Exchange/SEBI"],
    "disclosure": ["Reporting to Exchange/SEBI", "Record-Keeping & Documentation"],
    "systems_process": ["Cybersecurity & IT Infrastructure"],
    "timeline": ["Record-Keeping & Documentation"],
    "risk_management": ["Margin & Risk Management"],
    "grievance_redressal": ["Investor Grievance Redressal"],
    "cybersecurity": ["Cybersecurity & IT Infrastructure"],
    "advertising": ["Advertising & Marketing"],
    "record_keeping": ["Record-Keeping & Documentation"],
}


async def map_obligation_to_processes(obligation: Obligation, db: Session, use_llm: bool = True) -> list[ObligationProcessMap]:
    """Map a single obligation to its relevant operational processes."""
    mappings = []

    if use_llm:
        try:
            prompt = PROCESS_MAPPING_PROMPT.format(
                obligation_id=obligation.obligation_id,
                summary=obligation.obligation_text_summary,
                obligation_type=obligation.obligation_type,
                trigger_condition=obligation.trigger_condition or "N/A",
            )
            result = await generate_json(prompt)
            if isinstance(result, list):
                for item in result:
                    process_name = item.get("process_name", "")
                    # Validate against canonical list
                    matched = next((p for p in PROCESS_AREAS if p.lower() in process_name.lower() or process_name.lower() in p.lower()), None)
                    if matched:
                        mapping = ObligationProcessMap(
                            obligation_id=obligation.id,
                            process_name=matched,
                            confidence=item.get("confidence", 0.8),
                            is_override=False,
                            mapped_by="llm",
                        )
                        mappings.append(mapping)
        except Exception as e:
            logger.warning(f"LLM mapping failed for {obligation.obligation_id}, falling back to rules: {e}")

    # Fallback to rule-based mapping if LLM returned nothing
    if not mappings:
        fallback_processes = TYPE_TO_PROCESS.get(obligation.obligation_type, ["Record-Keeping & Documentation"])
        for proc in fallback_processes:
            mapping = ObligationProcessMap(
                obligation_id=obligation.id,
                process_name=proc,
                confidence=0.7,
                is_override=False,
                mapped_by="rule_engine",
            )
            mappings.append(mapping)

    for m in mappings:
        db.add(m)

    db.commit()
    return mappings


async def map_all_obligations(db: Session, use_llm: bool = True) -> int:
    """Map all unmapped obligations to processes."""
    unmapped = db.query(Obligation).filter(
        ~Obligation.id.in_(
            db.query(ObligationProcessMap.obligation_id).distinct()
        )
    ).all()

    count = 0
    for obl in unmapped:
        await map_obligation_to_processes(obl, db, use_llm)
        count += 1

    logger.info(f"Mapped {count} obligations to processes")
    return count


def override_process_mapping(obligation_id: int, process_name: str, user: str, db: Session) -> ObligationProcessMap:
    """Allow a user to manually override a process mapping."""
    mapping = ObligationProcessMap(
        obligation_id=obligation_id,
        process_name=process_name,
        confidence=1.0,
        is_override=True,
        mapped_by=user,
    )
    db.add(mapping)

    audit = AuditLog(
        entity_type="process_map",
        entity_id=str(obligation_id),
        action="override",
        new_value=process_name,
        user=user,
        timestamp=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    return mapping
