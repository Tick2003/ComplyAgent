"""Ingestion router — Module A: upload and parse SEBI circulars."""
import os
import shutil
import logging
from datetime import date
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.circular import Circular, ClauseChunk
from app.schemas import CircularOut, ClauseChunkOut
from app.services.parser import parse_circular_pdf
from app.services.extractor import extract_obligations_from_chunks
from app.services.mapper import map_all_obligations
from app.vector_store.store import add_chunks_to_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])


@router.post("/upload", response_model=CircularOut)
async def upload_circular(
    file: UploadFile = File(...),
    title: str = Form(...),
    circular_number: str = Form(None),
    effective_date: str = Form(None),
    circular_type: str = Form("master_circular"),
    db: Session = Depends(get_db),
):
    """Upload a SEBI circular PDF, parse it, extract obligations."""
    # Save the uploaded file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse effective date
    eff_date = None
    if effective_date:
        try:
            eff_date = date.fromisoformat(effective_date)
        except ValueError:
            pass

    # Create circular record
    circular = Circular(
        title=title,
        circular_number=circular_number,
        pdf_path=file_path,
        effective_date=eff_date,
        circular_type=circular_type,
        status="parsing",
    )
    db.add(circular)
    db.commit()
    db.refresh(circular)

    try:
        # Parse PDF into chunks
        chunks = parse_circular_pdf(file_path, title, eff_date, circular.id)

        # Store chunks in DB
        for chunk_data in chunks:
            chunk = ClauseChunk(**chunk_data)
            db.add(chunk)
        db.commit()

        # Add to vector store for RAG
        add_chunks_to_store(chunks)

        circular.status = "parsed"
        db.commit()

        # Extract obligations using LLM
        circular.status = "extracting"
        db.commit()

        obligations = await extract_obligations_from_chunks(chunks, circular.id, db)

        # Map obligations to processes
        await map_all_obligations(db, use_llm=True)

        circular.status = "extracted"
        circular.summary = f"Parsed {len(chunks)} clauses, extracted {len(obligations)} obligations."
        db.commit()

    except Exception as e:
        logger.error(f"Pipeline failed for circular {circular.id}: {e}")
        circular.status = "failed"
        circular.summary = f"Error: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    db.refresh(circular)
    return _circular_to_out(circular, db)


@router.get("/circulars", response_model=list[CircularOut])
def list_circulars(db: Session = Depends(get_db)):
    """List all ingested circulars."""
    circulars = db.query(Circular).order_by(Circular.upload_date.desc()).all()
    return [_circular_to_out(c, db) for c in circulars]


@router.get("/circulars/{circular_id}", response_model=CircularOut)
def get_circular(circular_id: int, db: Session = Depends(get_db)):
    """Get a specific circular by ID."""
    circular = db.query(Circular).filter(Circular.id == circular_id).first()
    if not circular:
        raise HTTPException(status_code=404, detail="Circular not found")
    return _circular_to_out(circular, db)


@router.get("/circulars/{circular_id}/chunks", response_model=list[ClauseChunkOut])
def get_circular_chunks(circular_id: int, db: Session = Depends(get_db)):
    """Get all parsed chunks for a circular."""
    chunks = db.query(ClauseChunk).filter(ClauseChunk.circular_id == circular_id).all()
    return chunks


def _circular_to_out(circular: Circular, db: Session) -> CircularOut:
    """Convert Circular model to output schema with computed fields."""
    from app.models.obligation import Obligation
    chunk_count = db.query(ClauseChunk).filter(ClauseChunk.circular_id == circular.id).count()
    obl_count = db.query(Obligation).filter(Obligation.circular_id == circular.id).count()
    return CircularOut(
        id=circular.id,
        title=circular.title,
        circular_number=circular.circular_number,
        source_url=circular.source_url,
        effective_date=circular.effective_date,
        upload_date=circular.upload_date,
        status=circular.status,
        circular_type=circular.circular_type,
        summary=circular.summary,
        chunk_count=chunk_count,
        obligation_count=obl_count,
    )
