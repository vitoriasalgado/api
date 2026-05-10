from httpx import AsyncClient


async def test_echo_ok(client: AsyncClient) -> None:
    response = await client.post("/api/v1/echo", json={"text": "oi", "repeat": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "oioioi"


async def test_echo_invalid_repeat(client: AsyncClient) -> None:
    response = await client.post("/api/v1/echo", json={"text": "oi", "repeat": 0})
    assert response.status_code == 422
