"""Google Maps results database model."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.internal.model.entity.base import Base

if TYPE_CHECKING:
    from src.internal.model.entity.gmaps_jobs import GmapsJob


class GmapsResult(Base):
    """Google Maps scraped result (POI) model."""

    __tablename__ = "gmaps_results"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign key to job
    job_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("gmaps_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Associated job ID",
    )

    # Place identification
    place_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Google Maps place ID (CID)",
    )
    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        comment="Place name",
    )

    # Address information
    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Full address",
    )
    street_address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Street address",
    )
    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="City",
    )
    state: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="State/Province",
    )
    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Country",
    )
    postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Postal/ZIP code",
    )

    # Geospatial data (PostGIS)
    coordinates: Mapped[Geometry] = mapped_column(
        Geometry("POINT", srid=4326),
        nullable=False,
        index=True,
        comment="Place coordinates (latitude, longitude) as PostGIS Point",
    )
    latitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
        nullable=False,
        comment="Latitude",
    )
    longitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
        nullable=False,
        comment="Longitude",
    )

    # H3 geospatial indexing
    h3_cell: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="H3 cell identifier for geospatial indexing",
    )

    # Contact information
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Phone number",
    )
    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Website URL",
    )

    # Additional data
    rating: Mapped[float | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        index=True,
        comment="Place rating (0-5)",
    )
    review_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of reviews",
    )
    category: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Place category",
    )
    types: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of place types",
    )

    # Metadata
    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional metadata as JSON",
    )
    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="Source Google Maps URL",
    )

    # Timestamps
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Scraping timestamp",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Soft delete timestamp",
    )

    # Relationships
    job: Mapped["GmapsJob | None"] = relationship(
        "GmapsJob",
        back_populates="results",
        lazy="selectin",
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("place_id", name="uq_gmaps_results_place_id"),
        Index("idx_results_coordinates", "coordinates", postgresql_using="gist"),
        Index("idx_results_h3_scraped", "h3_cell", "scraped_at"),
        Index("idx_results_category_rating", "category", "rating"),
        Index("idx_results_city_country", "city", "country"),
        Index("idx_results_deleted", "deleted_at"),
        {"comment": "Google Maps scraped results (POIs) table"},
    )

    def __repr__(self) -> str:
        return f"<GmapsResult(id={self.id}, name={self.name}, place_id={self.place_id})>"
