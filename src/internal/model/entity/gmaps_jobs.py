"""Google Maps jobs database model."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SQLEnum,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.internal.model.entity.base import Base

if TYPE_CHECKING:
    from src.internal.model.entity.gmaps_results import GmapsResult


class JobType(str, Enum):
    """Job type enumeration."""

    SEARCH = "SEARCH"  # Search for places in H3 cell
    PLACE = "PLACE"  # Get place details


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class GmapsJob(Base):
    """Google Maps scraping job model."""

    __tablename__ = "gmaps_jobs"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Job identification
    job_type: Mapped[JobType] = mapped_column(
        SQLEnum(JobType, native_enum=False),
        nullable=False,
        index=True,
        comment="Type of job: SEARCH or PLACE",
    )

    # Status tracking
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, native_enum=False),
        nullable=False,
        default=JobStatus.PENDING,
        index=True,
        comment="Current job status",
    )

    # H3 geospatial indexing
    h3_cell: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="H3 cell identifier for geospatial indexing",
    )

    # Search parameters
    category: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Place category (e.g., 'restaurant', 'hotel')",
    )
    keyword: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Search keyword",
    )

    # Job payload (flexible JSON storage)
    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional job parameters as JSON",
    )

    # Priority and scheduling
    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True,
        comment="Job priority (higher = more important)",
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Scheduled execution time (for delayed jobs)",
    )

    # Retry management
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of retry attempts",
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
        comment="Maximum retry attempts",
    )

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if job failed",
    )
    error_traceback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error traceback if job failed",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Job creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Job start timestamp",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Job completion timestamp",
    )

    # Relationships
    results: Mapped[list["GmapsResult"]] = relationship(
        "GmapsResult",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_jobs_status_created", "status", "created_at"),
        Index("idx_jobs_h3_status", "h3_cell", "status"),
        Index("idx_jobs_scheduled", "scheduled_at", "status"),
        Index("idx_jobs_priority_status", "priority", "status", "created_at"),
        {"comment": "Google Maps scraping jobs table"},
    )

    def __repr__(self) -> str:
        return f"<GmapsJob(id={self.id}, type={self.job_type}, status={self.status})>"
