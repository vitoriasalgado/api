from httpx import AsyncClient


async def test_create_materia_returns_201(client: AsyncClient) -> None:
    response = await client.post("/api/v1/materias", json={"name": "Matemática"})
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Matemática"


async def test_create_materia_returns_422_without_name(client: AsyncClient) -> None:
    response = await client.post("/api/v1/materias", json={})
    assert response.status_code == 422


async def test_list_materias_returns_all(client: AsyncClient) -> None:
    await client.post("/api/v1/materias", json={"name": "Matemática"})
    await client.post("/api/v1/materias", json={"name": "História"})

    response = await client.get("/api/v1/materias")

    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_get_materia_returns_200(client: AsyncClient) -> None:
    await client.post("/api/v1/materias", json={"name": "Matemática"})

    response = await client.get("/api/v1/materias/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Matemática"


async def test_get_materia_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/materias/999")
    assert response.status_code == 404


async def test_patch_materia_updates_name(client: AsyncClient) -> None:
    await client.post("/api/v1/materias", json={"name": "Mat"})

    response = await client.patch("/api/v1/materias/1", json={"name": "Matemática"})

    assert response.status_code == 200
    assert response.json()["name"] == "Matemática"


async def test_patch_materia_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.patch("/api/v1/materias/999", json={"name": "qualquer"})
    assert response.status_code == 404


async def test_delete_materia_returns_204(client: AsyncClient) -> None:
    await client.post("/api/v1/materias", json={"name": "Matemática"})

    response = await client.delete("/api/v1/materias/1")

    assert response.status_code == 204

    follow_up = await client.get("/api/v1/materias/1")
    assert follow_up.status_code == 404


async def test_delete_materia_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/materias/999")
    assert response.status_code == 404
