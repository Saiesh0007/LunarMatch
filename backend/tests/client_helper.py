import asyncio
from typing import Any, Dict, Optional
import httpx
from app.main import app

class AsyncTestClient:
    def __init__(self):
        self.transport = httpx.ASGITransport(app=app)
        self.base_url = "http://testserver"

    def get(self, url: str, **kwargs):
        async def _call():
            async with httpx.AsyncClient(transport=self.transport, base_url=self.base_url) as client:
                return await client.get(url, **kwargs)
        return asyncio.run(_call())

    def post(self, url: str, **kwargs):
        async def _call():
            async with httpx.AsyncClient(transport=self.transport, base_url=self.base_url) as client:
                return await client.post(url, **kwargs)
        return asyncio.run(_call())

test_client = AsyncTestClient()
