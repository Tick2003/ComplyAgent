"""Circular and ClauseChunk models — Module A storage."""
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class CircularStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    REVIEWED = "reviewed"
    FAILED = "failed"


class Circular(Base):
    __tablename__ = "circulars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500))
    circular_number: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(1000))
    pdf_path: Mapped[str | None] = mapped_column(String(500))
    effective_date: Mapped[date | None] = mapped_column(Date)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), default=CircularStatus.UPLOADED.value)
    circular_type: Mapped[str] = mapped_column(String(100), default="master_circular")  # master_circular | amendment
    summary: Mapped[str | None] = mapped_column(Text)

    # Relationships
    chunks: Mapped[list["ClauseChunk"]] = relationship(back_populates="circular", cascade="all, delete-orphan")


class ClauseChunk(Base):
    __tablename__ = "clause_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    circular_id: Mapped[int] = mapped_column(ForeignKey("circulars.id"))
    chunk_id: Mapped[str] = mapped_column(String(100), unique=True)
    chapter: Mapped[str | None] = mapped_column(String(500))
    section_id: Mapped[str | None] = mapped_column(String(50))
    page_number: Mapped[int | None] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    effective_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    circular: Mapped["Circular"] = relationship(back_populates="chunks")
