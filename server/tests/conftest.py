import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
def client():
    """Synchronous FastAPI test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client():
    """Async HTTPX client for testing async endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac