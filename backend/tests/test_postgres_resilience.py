import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import postgres


def test_create_pool_returns_none_when_database_unavailable(monkeypatch):
    async def fake_create_pool(*args, **kwargs):
        raise OSError("getaddrinfo failed")

    monkeypatch.setattr(postgres.asyncpg, "create_pool", fake_create_pool)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    result = asyncio.run(postgres.create_pool())

    assert result is None
    assert postgres.pool is None


def test_get_db_raises_http_exception_when_pool_missing():
    postgres.pool = None

    async def consume_db():
        async for _ in postgres.get_db():
            pass

    with pytest.raises(HTTPException):
        asyncio.run(consume_db())
