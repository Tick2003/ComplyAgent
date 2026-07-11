"""Obligation and process-mapping models — Module B & C storage."""
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    obligation_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    source_chunk_id: Mapped[str | None] = mapped_column(String(100), index=True)
    circular_id: Mapped[int | None] = mapped_column(ForeignKey("circulars.id"))
    source_clause_ref: Mapped[str | None] = mapped_column(String(500))
    obligation_text_summary: Mapped[str] = mapped_column(Text)
    applicable_intermediary: Mapped[str] = mapped_column(JSON, default=lambda: ["Stockbroker"])
    obligation_type: Mapped[str] = mapped_column(String(100))  # reporting, disclosure, etc.
    trigger_condition: Mapped[str | None] = mapped_column(Text)
    frequency: Mapped[str] = mapped_column(String(50), default="event-based")
    deadline_rule: Mapped[str | None] = mapped_column(Text)
    evidence_required: Mapped[str | None] = mapped_column(JSON)  # list of strings
    penalty_or_risk_if_noncompliant: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Review status
    review_status: Mapped[str] = mapped_column(String(50), default="pending_review")  # pending_review | approved | rejected
    reviewed_by: Mapped[str | None] = mapped_column(String(100))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    review_notes: Mapped[str | None] = mapped_column(Text)

    # Lifecycle
    status: Mapped[str] = mapped_column(String(50), default="active")  # active | superseded | repealed
    superseded_by: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    process_maps: Mapped[list["ObligationProcessMap"]] = relationship(back_populates="obligation", cascade="all, delete-orphan")
    evidence_items: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="obligation", cascade="all, delete-orphan")
    compliance_statuses: Mapped[list["ComplianceStatus"]] = relationship("ComplianceStatus", back_populates="obligation", cascade="all, delete-orphan")


class ObligationProcessMap(Base):
    __tablename__ = "obligation_process_map"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    obligation_id: Mapped[int] = mapped_column(ForeignKey("obligations.id"))
    process_name: Mapped[str] = mapped_column(String(200))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_override: Mapped[bool] = mapped_column(Boolean, default=False)
    mapped_by: Mapped[str | None] = mapped_column(String(100))
    mapped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    obligation: Mapped["Obligation"] = relationship(back_populates="process_maps")
