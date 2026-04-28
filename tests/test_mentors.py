import pytest
from httpx import AsyncClient

from app.api.routes import mentors


@pytest.fixture(autouse=True)
def reset_mentors_db():
    mentors.mentors_db.clear()
    mentors.next_id = 1
    yield


async def test_create_mentor_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/mentors",
        json={"name": "Ana", "expertise": "Python", "bio": "backend"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Ana"


async def test_list_mentors_returns_all(client: AsyncClient) -> None:
    await client.post("/api/v1/mentors", json={"name": "Ana", "expertise": "Python"})
    await client.post("/api/v1/mentors", json={"name": "João", "expertise": "Go"})

    response = await client.get("/api/v1/mentors")

    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_get_mentor_returns_200(client: AsyncClient) -> None:
    await client.post("/api/v1/mentors", json={"name": "Ana", "expertise": "Python"})

    response = await client.get("/api/v1/mentors/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Ana"


async def test_get_mentor_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/mentors/999")
    assert response.status_code == 404


async def test_patch_mentor_updates_only_sent_fields(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/mentors",
        json={"name": "Ana", "expertise": "Python", "bio": "antiga"},
    )

    response = await client.patch("/api/v1/mentors/1", json={"bio": "nova"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ana"
    assert body["expertise"] == "Python"
    assert body["bio"] == "nova"


async def test_patch_mentor_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.patch("/api/v1/mentors/999", json={"bio": "qualquer"})
    assert response.status_code == 404


async def test_delete_mentor_returns_204(client: AsyncClient) -> None:
    await client.post("/api/v1/mentors", json={"name": "Ana", "expertise": "Python"})

    response = await client.delete("/api/v1/mentors/1")

    assert response.status_code == 204

    follow_up = await client.get("/api/v1/mentors/1")
    assert follow_up.status_code == 404


async def test_delete_mentor_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/mentors/999")
    assert response.status_code == 404

