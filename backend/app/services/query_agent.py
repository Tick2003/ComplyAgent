"""Query Agent — RAG-based natural language Q&A over the obligation set."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.llm.client import generate_text
from app.llm.prompts import QUERY_AGENT_SYSTEM, QUERY_AGENT_PROMPT
from app.models.obligation import Obligation
from app.models.evidence import ComplianceStatus
from app.vector_store.store import query_store

logger = logging.getLogger(__name__)


async def answer_query(question: str, db: Session) -> dict:
    """
    Answer a natural-language compliance question using RAG:
    1. Retrieve relevant clause chunks from vector store
    2. Find related obligations and their current status
    3. Generate an answer with citations
    """
    # Step 1: Retrieve relevant clauses from vector store
    relevant_chunks = query_store(question, n_results=5)

    # Step 2: Find obligations linked to these chunks
    related_obligations = []
    chunk_ids = [c.get("chunk_id", "") for c in relevant_chunks]

    for chunk_id in chunk_ids:
        if not chunk_id:
            continue
        obls = db.query(Obligation).filter(
            Obligation.source_chunk_id == chunk_id,
            Obligation.status == "active",
        ).all()

        for obl in obls:
            # Get current compliance status
            current_status = (
                db.query(ComplianceStatus)
                .filter(ComplianceStatus.obligation_id == obl.id)
                .order_by(desc(ComplianceStatus.changed_at))
                .first()
            )

            related_obligations.append({
                "obligation_id": obl.obligation_id,
                "summary": obl.obligation_text_summary,
                "type": obl.obligation_type,
                "deadline_rule": obl.deadline_rule,
                "current_status": current_status.status if current_status else "unknown",
                "source_clause_ref": obl.source_clause_ref,
                "frequency": obl.frequency,
            })

    # Also search obligations directly by keyword
    keyword_obls = db.query(Obligation).filter(
        Obligation.status == "active",
        Obligation.obligation_text_summary.ilike(f"%{question.split()[0] if question.split() else ''}%"),
    ).limit(5).all()

    for obl in keyword_obls:
        if not any(r["obligation_id"] == obl.obligation_id for r in related_obligations):
            current_status = (
                db.query(ComplianceStatus)
                .filter(ComplianceStatus.obligation_id == obl.id)
                .order_by(desc(ComplianceStatus.changed_at))
                .first()
            )
            related_obligations.append({
                "obligation_id": obl.obligation_id,
                "summary": obl.obligation_text_summary,
                "type": obl.obligation_type,
                "deadline_rule": obl.deadline_rule,
                "current_status": current_status.status if current_status else "unknown",
                "source_clause_ref": obl.source_clause_ref,
                "frequency": obl.frequency,
            })

    # Step 3: Generate answer with LLM
    context_clauses = "\n\n".join([
        f"[{c.get('chapter', 'Unknown')}, Section {c.get('section_id', 'N/A')}]\n{c.get('text', '')}"
        for c in relevant_chunks
    ])

    obligation_data = "\n".join([
        f"- {o['obligation_id']}: {o['summary']} | Status: {o['current_status']} | Deadline: {o.get('deadline_rule', 'N/A')} | Ref: {o.get('source_clause_ref', 'N/A')}"
        for o in related_obligations
    ])

    prompt = QUERY_AGENT_PROMPT.format(
        context_clauses=context_clauses or "No specific regulatory clauses found for this query.",
        obligation_data=obligation_data or "No related obligations found.",
        question=question,
    )

    try:
        answer = await generate_text(prompt, system_instruction=QUERY_AGENT_SYSTEM)
    except Exception as e:
        logger.error(f"Query agent LLM call failed: {e}")
        answer = "I was unable to generate an answer at this time. Please try rephrasing your question."

    # Build citations
    citations = [
        {
            "chunk_id": c.get("chunk_id", ""),
            "chapter": c.get("chapter", ""),
            "section_id": c.get("section_id", ""),
            "text_preview": c.get("text", "")[:200],
            "relevance_score": c.get("relevance_score", 0),
        }
        for c in relevant_chunks
    ]

    return {
        "answer": answer,
        "citations": citations,
        "related_obligations": related_obligations,
        "confidence": sum(c.get("relevance_score", 0) for c in relevant_chunks) / max(len(relevant_chunks), 1),
    }
