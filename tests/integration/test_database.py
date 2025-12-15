"""Integration tests for database connection manager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.internal.store.database import (
    DatabaseManager,
    get_database_manager,
    reset_database_manager,
)


class TestDatabaseManager:
    """Tests for DatabaseManager."""

    def test_initialization(self, test_settings):
        """Test DatabaseManager initialization."""
        reset_database_manager()
        manager = get_database_manager()

        assert manager is not None
        assert isinstance(manager, DatabaseManager)

    def test_engine_not_initialized_error(self, test_db_manager):
        """Test that accessing engine before connect raises error."""
        with pytest.raises(RuntimeError, match="Database engine not initialized"):
            _ = test_db_manager.engine

    def test_session_factory_not_initialized_error(self, test_db_manager):
        """Test that accessing session_factory before connect raises error."""
        with pytest.raises(RuntimeError, match="Session factory not initialized"):
            _ = test_db_manager.session_factory

    @pytest.mark.asyncio
    async def test_connect_success(self, test_db_manager):
        """Test successful database connection."""
        # Mock the engine creation to avoid actual database connection
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_create_engine.return_value = mock_engine

            mock_session_factory = MagicMock()
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()

            assert test_db_manager._engine is not None
            assert test_db_manager._session_factory is not None

    @pytest.mark.asyncio
    async def test_connect_already_initialized(self, test_db_manager):
        """Test that connecting twice doesn't raise error."""
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_create_engine.return_value = mock_engine

            mock_session_factory = MagicMock()
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()
            await test_db_manager.connect()  # Should not raise error

    @pytest.mark.asyncio
    async def test_disconnect(self, test_db_manager):
        """Test database disconnection."""
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_engine.dispose = AsyncMock()
            mock_create_engine.return_value = mock_engine

            mock_session_factory = MagicMock()
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()
            await test_db_manager.disconnect()

            assert test_db_manager._engine is None
            assert test_db_manager._session_factory is None
            mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, test_db_manager):
        """Test disconnecting when not connected doesn't raise error."""
        await test_db_manager.disconnect()  # Should not raise error

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, test_db_manager):
        """Test health check when not connected."""
        result = await test_db_manager.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_success(self, test_db_manager):
        """Test successful health check."""
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_create_engine.return_value = mock_engine

            mock_session_factory = MagicMock()
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()
            result = await test_db_manager.health_check()

            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, test_db_manager):
        """Test health check failure."""
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            # First, setup successful connection
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_create_engine.return_value = mock_engine

            mock_session_factory = MagicMock()
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()

            # Now make health_check fail
            mock_conn.execute = AsyncMock(side_effect=Exception("Connection failed"))
            result = await test_db_manager.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_get_session_context_manager(self, test_db_manager):
        """Test get_session as async context manager."""
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_create_engine.return_value = mock_engine

            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.commit = AsyncMock()
            mock_session.close = AsyncMock()
            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory = MagicMock(return_value=mock_session_ctx)
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()

            async with test_db_manager.get_session() as session:
                assert session is not None

            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_rollback_on_error(self, test_db_manager):
        """Test that session rolls back on error."""
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_create_engine.return_value = mock_engine

            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.rollback = AsyncMock()
            mock_session.close = AsyncMock()
            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory = MagicMock(return_value=mock_session_ctx)
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()

            with pytest.raises(ValueError):
                async with test_db_manager.get_session() as session:
                    raise ValueError("Test error")

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_pool_size_property(self, test_db_manager):
        """Test pool_size property."""
        size = test_db_manager.pool_size
        assert isinstance(size, int)
        assert size >= 0

    def test_is_connected_property(self, test_db_manager):
        """Test is_connected property."""
        assert test_db_manager.is_connected is False

    @pytest.mark.asyncio
    async def test_is_connected_after_connect(self, test_db_manager):
        """Test is_connected after connection."""
        with patch(
            "src.internal.store.database.database.create_async_engine"
        ) as mock_create_engine, patch(
            "src.internal.store.database.database.async_sessionmaker"
        ) as mock_sessionmaker:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute = AsyncMock(return_value=mock_result)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin = MagicMock(return_value=mock_context)
            mock_create_engine.return_value = mock_engine

            mock_session_factory = MagicMock()
            mock_sessionmaker.return_value = mock_session_factory

            await test_db_manager.connect()
            assert test_db_manager.is_connected is True


class TestDatabaseManagerSingleton:
    """Tests for DatabaseManager singleton pattern."""

    def test_get_database_manager_singleton(self):
        """Test that get_database_manager returns the same instance."""
        reset_database_manager()
        manager1 = get_database_manager()
        manager2 = get_database_manager()
        assert manager1 is manager2

    def test_reset_database_manager(self):
        """Test that reset_database_manager creates a new instance."""
        reset_database_manager()
        manager1 = get_database_manager()
        reset_database_manager()
        manager2 = get_database_manager()
        assert manager1 is not manager2
