from collections.abc import AsyncIterator
import sys

import httpx
import pytest

from api_gateway.app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    if sys.version_info >= (3, 14):
        pytest.skip(
            "ASGI request clients currently hang under the local Python 3.14 runtime; "
            "request-level coverage remains enabled in CI on Python 3.11.",
        )

    await app.router.startup()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
    await app.router.shutdown()
