from httpx import AsyncClient


async def test_ping_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/ping")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "pong"
