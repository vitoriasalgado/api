from httpx import AsyncClient


async def _seed_aluno_e_materia(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/materias", json={"name": "Matemática"})


async def test_create_nota_returns_201(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)

    response = await client.post(
        "/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 8.5}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["valor"] == 8.5


async def test_create_nota_returns_422_when_valor_above_10(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)

    response = await client.post(
        "/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 15}
    )

    assert response.status_code == 422


async def test_create_nota_returns_422_when_valor_below_0(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)

    response = await client.post(
        "/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": -1}
    )

    assert response.status_code == 422


async def test_create_nota_returns_422_without_required_fields(client: AsyncClient) -> None:
    response = await client.post("/api/v1/notas", json={"valor": 8})
    assert response.status_code == 422


async def test_create_nota_returns_404_when_aluno_does_not_exist(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)

    response = await client.post(
        "/api/v1/notas", json={"aluno_id": 999, "materia_id": 1, "valor": 8}
    )

    assert response.status_code == 404


async def test_create_nota_returns_404_when_materia_does_not_exist(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)

    response = await client.post(
        "/api/v1/notas", json={"aluno_id": 999, "materia_id": 1, "valor": 8}
    )

    assert response.status_code == 404


async def test_list_notas_returns_all(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 8})
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 9})

    response = await client.get("/api/v1/notas")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_list_notas_filtra_por_aluno_id(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "A1", "email": "a1@t.com"})
    await client.post("/api/v1/alunos", json={"name": "A2", "email": "a2@t.com"})
    await client.post("/api/v1/materias", json={"name": "Mat"})
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 8})
    await client.post("/api/v1/notas", json={"aluno_id": 2, "materia_id": 1, "valor": 9})

    response = await client.get("/api/v1/notas?aluno_id=1")

    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 1
    assert body["items"][0]["aluno_id"] == 1


async def test_list_notas_filtra_por_aluno_e_materia(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "A", "email": "a@t.com"})
    await client.post("/api/v1/materias", json={"name": "M1"})
    await client.post("/api/v1/materias", json={"name": "M2"})
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 8})
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 2, "valor": 7})

    response = await client.get("/api/v1/notas?aluno_id=1&materia_id=2")

    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 1
    assert body["items"][0]["materia_id"] == 2


async def test_list_notas_ordena_por_valor_desc(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 5})
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 9})
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 7})

    response = await client.get("/api/v1/notas?sort=-valor")

    body = response.json()
    assert response.status_code == 200
    assert [n["valor"] for n in body["items"]] == [9, 7, 5]


async def test_get_nota_returns_200(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 8})

    response = await client.get("/api/v1/notas/1")

    assert response.status_code == 200
    assert response.json()["valor"] == 8


async def test_get_nota_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/notas/999")
    assert response.status_code == 404


async def test_patch_nota_updates_valor(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 5})

    response = await client.patch("/api/v1/notas/1", json={"valor": 9.5})

    assert response.status_code == 200
    assert response.json()["valor"] == 9.5


async def test_patch_nota_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.patch("/api/v1/notas/999", json={"valor": 5})
    assert response.status_code == 404


async def test_delete_nota_returns_204(client: AsyncClient) -> None:
    await _seed_aluno_e_materia(client)
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 8})

    response = await client.delete("/api/v1/notas/1")

    assert response.status_code == 204

    follow_up = await client.get("/api/v1/notas/1")
    assert follow_up.status_code == 404


async def test_delete_nota_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/notas/999")
    assert response.status_code == 404
