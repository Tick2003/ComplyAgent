"""Agents router — Module E: Change Detection, Gap-Finder, Query Agent."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import QueryRequest, QueryResponse, GapReport, ChangeDetectionResult
from app.services.change_agent import detect_changes
from app.services.gap_agent import find_gaps
from app.services.query_agent import answer_query
from app.models.circular import ClauseChunk

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest, db: Session = Depends(get_db)):
    """Natural language Q&A about compliance obligations (RAG-powered)."""
    result = await answer_query(request.question, db)
    return QueryResponse(**result)


@router.post("/gap-analysis", response_model=GapReport)
async def gap_analysis(db: Session = Depends(get_db)):
    """Run the Gap-Finder Agent — scans all obligations for compliance gaps."""
    result = await find_gaps(db)
    return GapReport(**result)


@router.post("/change-detection/{circular_id}", response_model=ChangeDetectionResult)
async def change_detection(circular_id: int, db: Session = Depends(get_db)):
    """
    Run Change Detection Agent on a specific circular.
    Compares its chunks against existing obligations.
    """
    chunks = db.query(ClauseChunk).filter(ClauseChunk.circular_id == circular_id).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for this circular")

    chunk_dicts = [
        {
            "chunk_id": c.chunk_id,
            "chapter": c.chapter,
            "section_id": c.section_id,
            "text": c.text,
            "page_number": c.page_number,
        }
        for c in chunks
    ]

    result = await detect_changes(chunk_dicts, db)
    return ChangeDetectionResult(**result)
