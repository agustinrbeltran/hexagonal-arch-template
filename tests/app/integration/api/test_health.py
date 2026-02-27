import httpx
import pytest


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_returns_200_with_status_ok(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
