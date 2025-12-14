"""Database connection manager."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DatabaseManager:
    """Async database connection manager."""

    def __init__(self) -> None:
        """Initialize database manager."""
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._settings = get_settings()

    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine."""
        if self._engine is None:
            raise RuntimeError("Database engine not initialized. Call connect() first.")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the session factory."""
        if self._session_factory is None:
            raise RuntimeError(
                "Session factory not initialized. Call connect() first."
            )
        return self._session_factory

    async def connect(self) -> None:
        """Initialize database engine and verify connection."""
        if self._engine is not None:
            logger.warning("Database engine already initialized")
            return

        db_config = self._settings.database
        database_url = db_config.database_url.strip()

        logger.info(
            "Connecting to database: %s:%s/%s",
            db_config.host,
            db_config.port,
            db_config.name,
        )

        # Create async engine with connection pooling
        self._engine = create_async_engine(
            database_url,
            pool_size=db_config.pool_size,
            max_overflow=db_config.max_overflow,
            pool_timeout=db_config.pool_timeout,
            pool_recycle=db_config.pool_recycle,
            pool_pre_ping=True,  # Verify connections before using
            echo=self._settings.debug,  # SQL logging in debug mode
            future=True,  # SQLAlchemy 2.0 compatibility
        )

        # Create session factory
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        # Verify connection
        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error("Failed to connect to database: %s", e)
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        """Close database engine and cleanup."""
        if self._engine is None:
            return

        logger.info("Disconnecting from database")
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None
        logger.info("Database disconnected")

    async def health_check(self) -> bool:
        """Check database connectivity."""
        if self._engine is None:
            return False

        try:
            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error("Database health check failed: %s", e)
            return False

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session as async context manager."""
        if self._session_factory is None:
            raise RuntimeError(
                "Session factory not initialized. Call connect() first."
            )

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def execute_in_transaction(
        self, func: Callable[[AsyncSession], AsyncGenerator[T, None]]
    ) -> T:
        """Execute a function within a database transaction."""
        async with self.get_session() as session:
            async_gen = func(session)
            try:
                result = await async_gen.__anext__()
                return result
            except StopAsyncIteration:
                raise RuntimeError("Function did not yield a result")
            finally:
                # Clean up generator
                try:
                    await async_gen.aclose()
                except Exception:
                    pass

    @property
    def pool_size(self) -> int:
        """Get configured pool size."""
        if self._engine is None:
            return 0
        return self._settings.database.pool_size

    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._engine is not None


# Global database manager instance
_database_manager: DatabaseManager | None = None


def get_database_manager() -> DatabaseManager:
    """Get or create the global database manager instance."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager


def reset_database_manager() -> None:
    """Reset the global database manager instance (useful for testing)."""
    global _database_manager
    _database_manager = None


# Convenience function for getting database sessions
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (convenience function)."""
    db_manager = get_database_manager()
    async with db_manager.get_session() as session:
        yield session
