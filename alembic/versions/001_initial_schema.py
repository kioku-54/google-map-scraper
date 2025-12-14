"""
Initial schema
    Revision ID: 001
    Revises:
    Create Date: 2024-12-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create gmaps_jobs table
    op.create_table(
        "gmaps_jobs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "job_type",
            sa.Enum("SEARCH", "PLACE", name="jobtype", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "PROCESSING",
                "COMPLETED",
                "FAILED",
                "CANCELLED",
                name="jobstatus",
                native_enum=False,
            ),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("h3_cell", sa.String(length=20), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("keyword", sa.String(length=255), nullable=True),
        sa.Column("payload", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("error_traceback", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        comment="Google Maps scraping jobs table",
    )

    # Create indexes for gmaps_jobs
    op.create_index("ix_gmaps_jobs_job_type", "gmaps_jobs", ["job_type"])
    op.create_index("ix_gmaps_jobs_status", "gmaps_jobs", ["status"])
    op.create_index("ix_gmaps_jobs_h3_cell", "gmaps_jobs", ["h3_cell"])
    op.create_index("ix_gmaps_jobs_category", "gmaps_jobs", ["category"])
    op.create_index("ix_gmaps_jobs_keyword", "gmaps_jobs", ["keyword"])
    op.create_index("ix_gmaps_jobs_priority", "gmaps_jobs", ["priority"])
    op.create_index("ix_gmaps_jobs_scheduled_at", "gmaps_jobs", ["scheduled_at"])
    op.create_index("ix_gmaps_jobs_created_at", "gmaps_jobs", ["created_at"])
    op.create_index("ix_gmaps_jobs_completed_at", "gmaps_jobs", ["completed_at"])
    op.create_index(
        "idx_jobs_status_created", "gmaps_jobs", ["status", "created_at"]
    )
    op.create_index("idx_jobs_h3_status", "gmaps_jobs", ["h3_cell", "status"])
    op.create_index(
        "idx_jobs_scheduled", "gmaps_jobs", ["scheduled_at", "status"]
    )
    op.create_index(
        "idx_jobs_priority_status",
        "gmaps_jobs",
        ["priority", "status", "created_at"],
    )

    # Create gmaps_results table
    op.create_table(
        "gmaps_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.BigInteger(), nullable=True),
        sa.Column("place_id", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("street_address", sa.String(length=500), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column(
            "coordinates",
            Geometry("POINT", srid=4326),
            nullable=False,
        ),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("h3_cell", sa.String(length=20), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("rating", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("types", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["gmaps_jobs.id"],
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("place_id", name="uq_gmaps_results_place_id"),
        comment="Google Maps scraped results (POIs) table",
    )

    # Create indexes for gmaps_results
    op.create_index("ix_gmaps_results_job_id", "gmaps_results", ["job_id"])
    op.create_index("ix_gmaps_results_place_id", "gmaps_results", ["place_id"])
    op.create_index("ix_gmaps_results_name", "gmaps_results", ["name"])
    op.create_index("ix_gmaps_results_city", "gmaps_results", ["city"])
    op.create_index("ix_gmaps_results_state", "gmaps_results", ["state"])
    op.create_index("ix_gmaps_results_country", "gmaps_results", ["country"])
    op.create_index("ix_gmaps_results_rating", "gmaps_results", ["rating"])
    op.create_index("ix_gmaps_results_category", "gmaps_results", ["category"])
    op.create_index("ix_gmaps_results_h3_cell", "gmaps_results", ["h3_cell"])
    op.create_index("ix_gmaps_results_scraped_at", "gmaps_results", ["scraped_at"])
    op.create_index("ix_gmaps_results_deleted_at", "gmaps_results", ["deleted_at"])

    # Create GIST index for coordinates (PostGIS)
    op.create_index(
        "idx_results_coordinates",
        "gmaps_results",
        ["coordinates"],
        postgresql_using="gist",
    )

    # Create composite indexes
    op.create_index(
        "idx_results_h3_scraped", "gmaps_results", ["h3_cell", "scraped_at"]
    )
    op.create_index(
        "idx_results_category_rating", "gmaps_results", ["category", "rating"]
    )
    op.create_index(
        "idx_results_city_country", "gmaps_results", ["city", "country"]
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_results_city_country", table_name="gmaps_results")
    op.drop_index("idx_results_category_rating", table_name="gmaps_results")
    op.drop_index("idx_results_h3_scraped", table_name="gmaps_results")
    op.drop_index("idx_results_coordinates", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_deleted_at", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_scraped_at", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_h3_cell", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_category", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_rating", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_country", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_state", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_city", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_name", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_place_id", table_name="gmaps_results")
    op.drop_index("ix_gmaps_results_job_id", table_name="gmaps_results")

    op.drop_index("idx_jobs_priority_status", table_name="gmaps_jobs")
    op.drop_index("idx_jobs_scheduled", table_name="gmaps_jobs")
    op.drop_index("idx_jobs_h3_status", table_name="gmaps_jobs")
    op.drop_index("idx_jobs_status_created", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_completed_at", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_created_at", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_scheduled_at", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_priority", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_keyword", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_category", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_h3_cell", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_status", table_name="gmaps_jobs")
    op.drop_index("ix_gmaps_jobs_job_type", table_name="gmaps_jobs")

    # Drop tables
    op.drop_table("gmaps_results")
    op.drop_table("gmaps_jobs")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.execute("DROP TYPE IF EXISTS jobtype")

    # Drop PostGIS extension (optional - comment out if you want to keep it)
    # op.execute("DROP EXTENSION IF EXISTS postgis")
