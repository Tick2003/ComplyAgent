"""Evidence and ComplianceStatus models — Module D (append-only ledger)."""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Evidence(Base):
    """Evidence attached to an obligation. Each row is immutable once created."""
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    obligation_id: Mapped[int] = mapped_column(ForeignKey("obligations.id"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(50))  # document | link | checkbox | data_feed
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)  # URL, file path, or description
    file_path: Mapped[str | None] = mapped_column(String(500))
    uploaded_by: Mapped[str] = mapped_column(String(100))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    obligation: Mapped["Obligation"] = relationship(back_populates="evidence_items")


class ComplianceStatus(Base):
    """Append-only status log. Current status = latest row per obligation_id."""
    __tablename__ = "compliance_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    obligation_id: Mapped[int] = mapped_column(ForeignKey("obligations.id"), index=True)
    status: Mapped[str] = mapped_column(String(50))  # compliant | partially_compliant | non_compliant | not_yet_due
    changed_by: Mapped[str] = mapped_column(String(100))
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    obligation: Mapped["Obligation"] = relationship(back_populates="compliance_statuses")
