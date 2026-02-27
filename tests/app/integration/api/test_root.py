import httpx
import pytest


class TestRootEndpoint:
    @pytest.mark.asyncio
    async def test_redirects_to_docs(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get("/", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "docs/"
