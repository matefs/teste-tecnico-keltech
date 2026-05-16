# Arquivo: tests/infrastructure/rabbitmq/test_connection.py
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import src.infrastructure.rabbitmq.connection as connection_module
from src.infrastructure.rabbitmq.connection import (
    close_rabbitmq_connection,
    get_rabbitmq_connection,
)


@pytest.fixture(autouse=True)
def reset_connection_singleton():
    connection_module._connection = None
    yield
    connection_module._connection = None


class TestGetRabbitmqConnection:
    async def test_creates_new_connection_when_none(self):
        mock_connection = MagicMock()

        with patch(
            "src.infrastructure.rabbitmq.connection.aio_pika.connect_robust",
            new=AsyncMock(return_value=mock_connection),
        ) as mock_connect:
            result = await get_rabbitmq_connection()

        mock_connect.assert_called_once()
        assert result is mock_connection

    async def test_returns_existing_connection_when_open(self):
        existing_connection = MagicMock()
        existing_connection.is_closed = False
        connection_module._connection = existing_connection

        with patch(
            "src.infrastructure.rabbitmq.connection.aio_pika.connect_robust",
            new=AsyncMock(),
        ) as mock_connect:
            result = await get_rabbitmq_connection()

        mock_connect.assert_not_called()
        assert result is existing_connection

    async def test_creates_new_connection_when_previous_is_closed(self):
        closed_connection = MagicMock()
        closed_connection.is_closed = True
        connection_module._connection = closed_connection

        new_connection = MagicMock()

        with patch(
            "src.infrastructure.rabbitmq.connection.aio_pika.connect_robust",
            new=AsyncMock(return_value=new_connection),
        ) as mock_connect:
            result = await get_rabbitmq_connection()

        mock_connect.assert_called_once()
        assert result is new_connection

    async def test_uses_rabbitmq_url_from_settings(self):
        from src.config.settings import settings

        with patch(
            "src.infrastructure.rabbitmq.connection.aio_pika.connect_robust",
            new=AsyncMock(return_value=MagicMock()),
        ) as mock_connect:
            await get_rabbitmq_connection()

        mock_connect.assert_called_once_with(settings.RABBITMQ_URL)


class TestCloseRabbitmqConnection:
    async def test_closes_open_connection_and_resets_to_none(self):
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.close = AsyncMock()
        connection_module._connection = mock_connection

        await close_rabbitmq_connection()

        mock_connection.close.assert_called_once()
        assert connection_module._connection is None

    async def test_does_nothing_when_connection_is_none(self):
        connection_module._connection = None

        await close_rabbitmq_connection()

        assert connection_module._connection is None

    async def test_does_not_close_already_closed_connection(self):
        mock_connection = MagicMock()
        mock_connection.is_closed = True
        mock_connection.close = AsyncMock()
        connection_module._connection = mock_connection

        await close_rabbitmq_connection()

        mock_connection.close.assert_not_called()
