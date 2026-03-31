#!/usr/bin/env python
"""Quick API test - no server needed, test via ASGI transport"""
from httpx import ASGITransport, AsyncClient
import asyncio

from src.api.main import app

async def test():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        print(f"Status: {r.status_code}")
        print(f"Body: {r.json()}")

        # Test create project (follow redirects)
        r2 = await client.post("/api/v1/projects", json={"name": "测试小说"}, follow_redirects=True)
        print(f"\nCreate project status: {r2.status_code}")
        if r2.status_code in (200, 201):
            print(f"Response: {r2.json()}")

        # Test list projects
        r3 = await client.get("/api/v1/projects", follow_redirects=True)
        print(f"\nList projects status: {r3.status_code}")
        if r3.status_code == 200:
            data = r3.json()
            print(f"Total: {data.get('total', 'N/A')}")
            if data.get('items'):
                print(f"First item: {data['items'][0]['name']}")

if __name__ == "__main__":
    asyncio.run(test())
