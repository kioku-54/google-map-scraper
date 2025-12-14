"""Tests for database models."""

import pytest
from datetime import datetime

from src.internal.model.entity.gmaps_jobs import GmapsJob, JobStatus, JobType
from src.internal.model.entity.gmaps_results import GmapsResult


class TestJobType:
    """Tests for JobType enum."""

    def test_job_type_values(self):
        """Test JobType enum values."""
        assert JobType.SEARCH == "SEARCH"
        assert JobType.PLACE == "PLACE"

    def test_job_type_members(self):
        """Test JobType enum members."""
        assert len(list(JobType)) == 2
        assert JobType.SEARCH in JobType
        assert JobType.PLACE in JobType


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_job_status_values(self):
        """Test JobStatus enum values."""
        assert JobStatus.PENDING == "PENDING"
        assert JobStatus.PROCESSING == "PROCESSING"
        assert JobStatus.COMPLETED == "COMPLETED"
        assert JobStatus.FAILED == "FAILED"
        assert JobStatus.CANCELLED == "CANCELLED"

    def test_job_status_members(self):
        """Test JobStatus enum members."""
        assert len(list(JobStatus)) == 5
        assert JobStatus.PENDING in JobStatus
        assert JobStatus.PROCESSING in JobStatus
        assert JobStatus.COMPLETED in JobStatus
        assert JobStatus.FAILED in JobStatus
        assert JobStatus.CANCELLED in JobStatus


class TestGmapsJob:
    """Tests for GmapsJob model."""

    def test_job_creation(self):
        """Test creating a GmapsJob instance."""
        job = GmapsJob(
            job_type=JobType.SEARCH,
            status=JobStatus.PENDING,
            h3_cell="8928308280fffff",
            category="restaurant",
            keyword="pizza",
            retry_count=0,
            max_retries=3,
            priority=0,
        )

        assert job.job_type == JobType.SEARCH
        assert job.status == JobStatus.PENDING
        assert job.h3_cell == "8928308280fffff"
        assert job.category == "restaurant"
        assert job.keyword == "pizza"
        assert job.retry_count == 0
        assert job.max_retries == 3
        assert job.priority == 0

    def test_job_default_status(self):
        """Test that job can be created with PENDING status."""
        job = GmapsJob(
            job_type=JobType.SEARCH,
            status=JobStatus.PENDING,
            retry_count=0,
            max_retries=3,
        )
        assert job.status == JobStatus.PENDING

    def test_job_repr(self):
        """Test GmapsJob __repr__ method."""
        job = GmapsJob(
            id=1,
            job_type=JobType.SEARCH,
            status=JobStatus.PENDING,
        )
        repr_str = repr(job)
        assert "GmapsJob" in repr_str
        assert "SEARCH" in repr_str
        assert "PENDING" in repr_str

    def test_job_with_payload(self):
        """Test job with JSON payload."""
        payload = {"key": "value", "number": 123}
        job = GmapsJob(
            job_type=JobType.PLACE,
            payload=payload,
        )

        assert job.payload == payload
        assert job.payload["key"] == "value"
        assert job.payload["number"] == 123

    def test_job_timestamps(self):
        """Test job timestamp fields."""
        now = datetime.now()
        job = GmapsJob(
            job_type=JobType.SEARCH,
            created_at=now,
            updated_at=now,
        )

        assert job.created_at == now
        assert job.updated_at == now
        assert job.started_at is None
        assert job.completed_at is None


class TestGmapsResult:
    """Tests for GmapsResult model."""

    def test_result_creation(self):
        """Test creating a GmapsResult instance."""
        from geoalchemy2 import WKTElement

        result = GmapsResult(
            name="Test Restaurant",
            place_id="ChIJ123456789",
            latitude=40.7128,
            longitude=-74.0060,
            coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
            city="New York",
            state="NY",
            country="USA",
        )

        assert result.name == "Test Restaurant"
        assert result.place_id == "ChIJ123456789"
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.city == "New York"
        assert result.state == "NY"
        assert result.country == "USA"

    def test_result_repr(self):
        """Test GmapsResult __repr__ method."""
        from geoalchemy2 import WKTElement

        result = GmapsResult(
            id=1,
            name="Test Place",
            place_id="ChIJ123",
            coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )
        repr_str = repr(result)
        assert "GmapsResult" in repr_str
        assert "Test Place" in repr_str
        assert "ChIJ123" in repr_str

    def test_result_with_rating(self):
        """Test result with rating data."""
        from geoalchemy2 import WKTElement

        result = GmapsResult(
            name="Test Place",
            coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
            rating=4.5,
            review_count=100,
        )

        assert result.rating == 4.5
        assert result.review_count == 100

    def test_result_with_metadata(self):
        """Test result with extra metadata."""
        from geoalchemy2 import WKTElement

        metadata = {"source": "google_maps", "scraped_by": "test"}
        result = GmapsResult(
            name="Test Place",
            coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
            extra_metadata=metadata,
        )

        assert result.extra_metadata == metadata
        assert result.extra_metadata["source"] == "google_maps"

    def test_result_soft_delete(self):
        """Test result soft delete pattern."""
        from geoalchemy2 import WKTElement

        result = GmapsResult(
            name="Test Place",
            coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )

        assert result.deleted_at is None

        # Simulate soft delete
        result.deleted_at = datetime.now()
        assert result.deleted_at is not None


class TestModelRelationships:
    """Tests for model relationships."""

    def test_job_results_relationship(self):
        """Test relationship between GmapsJob and GmapsResult."""
        from geoalchemy2 import WKTElement

        job = GmapsJob(
            id=1,
            job_type=JobType.SEARCH,
            status=JobStatus.COMPLETED,
        )

        result = GmapsResult(
            id=1,
            job_id=1,
            name="Test Place",
            coordinates=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )

        # Test relationship (would work with actual database session)
        assert result.job_id == job.id
