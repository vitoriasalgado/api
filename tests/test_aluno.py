from httpx import AsyncClient


async def test_create_aluno_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/alunos", json={"name": "Maria", "email": "maria@test.com"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["email"] == "maria@test.com"


async def test_create_aluno_returns_422_with_invalid_email(client: AsyncClient) -> None:
    response = await client.post("/api/v1/alunos", json={"name": "Maria", "email": "naoemail"})
    assert response.status_code == 422


async def test_create_aluno_returns_422_without_email(client: AsyncClient) -> None:
    response = await client.post("/api/v1/alunos", json={"name": "Maria"})
    assert response.status_code == 422


async def test_create_aluno_returns_409_when_email_duplicated(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "maria@test.com"})

    response = await client.post(
        "/api/v1/alunos", json={"name": "Outra", "email": "maria@test.com"}
    )

    assert response.status_code == 409


async def test_list_alunos_returns_all(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/alunos", json={"name": "João", "email": "j@t.com"})

    response = await client.get("/api/v1/alunos")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_list_alunos_respeita_skip_e_limit(client: AsyncClient) -> None:
    for i in range(5):
        await client.post("/api/v1/alunos", json={"name": f"A{i}", "email": f"a{i}@t.com"})

    response = await client.get("/api/v1/alunos?skip=2&limit=2")

    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 5
    assert body["skip"] == 2
    assert body["limit"] == 2
    assert len(body["items"]) == 2


async def test_list_alunos_limit_acima_do_teto_returns_422(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alunos?limit=1000")
    assert response.status_code == 422


async def test_list_alunos_filtra_por_materia_id(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "A1", "email": "a1@t.com"})
    await client.post("/api/v1/alunos", json={"name": "A2", "email": "a2@t.com"})
    await client.post("/api/v1/alunos", json={"name": "A3", "email": "a3@t.com"})
    await client.post("/api/v1/materias", json={"name": "Mat"})
    await client.post("/api/v1/alunos/1/materias/1")
    await client.post("/api/v1/alunos/2/materias/1")

    response = await client.get("/api/v1/alunos?materia_id=1")

    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 2
    assert {a["id"] for a in body["items"]} == {1, 2}


async def test_list_alunos_ordena_por_name_asc(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Carlos", "email": "c@t.com"})
    await client.post("/api/v1/alunos", json={"name": "Ana", "email": "a@t.com"})
    await client.post("/api/v1/alunos", json={"name": "Beatriz", "email": "b@t.com"})

    response = await client.get("/api/v1/alunos?sort=name")

    body = response.json()
    assert response.status_code == 200
    assert [a["name"] for a in body["items"]] == ["Ana", "Beatriz", "Carlos"]


async def test_list_alunos_ordena_por_name_desc(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Carlos", "email": "c@t.com"})
    await client.post("/api/v1/alunos", json={"name": "Ana", "email": "a@t.com"})

    response = await client.get("/api/v1/alunos?sort=-name")

    body = response.json()
    assert response.status_code == 200
    assert [a["name"] for a in body["items"]] == ["Carlos", "Ana"]


async def test_list_alunos_sort_invalido_returns_422(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alunos?sort=hackear")
    assert response.status_code == 422


async def test_get_aluno_returns_200(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})

    response = await client.get("/api/v1/alunos/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Maria"


async def test_get_aluno_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alunos/999")
    assert response.status_code == 404


async def test_patch_aluno_updates_name(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})

    response = await client.patch("/api/v1/alunos/1", json={"name": "Maria Silva"})

    assert response.status_code == 200
    assert response.json()["name"] == "Maria Silva"


async def test_patch_aluno_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.patch("/api/v1/alunos/999", json={"name": "qualquer"})
    assert response.status_code == 404


async def test_delete_aluno_returns_204(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})

    response = await client.delete("/api/v1/alunos/1")

    assert response.status_code == 204

    follow_up = await client.get("/api/v1/alunos/1")
    assert follow_up.status_code == 404


async def test_delete_aluno_returns_404_when_not_found(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/alunos/999")
    assert response.status_code == 404


async def test_matricular_aluno_em_materia_returns_204(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/materias", json={"name": "Matemática"})

    response = await client.post("/api/v1/alunos/1/materias/1")

    assert response.status_code == 204


async def test_listar_materias_do_aluno(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/materias", json={"name": "Mat"})
    await client.post("/api/v1/materias", json={"name": "Hist"})
    await client.post("/api/v1/alunos/1/materias/1")
    await client.post("/api/v1/alunos/1/materias/2")

    response = await client.get("/api/v1/alunos/1/materias")

    assert response.status_code == 200
    assert sorted(response.json()) == [1, 2]


async def test_matricular_duplicada_returns_409(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/materias", json={"name": "Mat"})
    await client.post("/api/v1/alunos/1/materias/1")

    response = await client.post("/api/v1/alunos/1/materias/1")

    assert response.status_code == 409


async def test_matricular_returns_404_when_aluno_does_not_exist(client: AsyncClient) -> None:
    await client.post("/api/v1/materias", json={"name": "Mat"})

    response = await client.post("/api/v1/alunos/999/materias/1")

    assert response.status_code == 404


async def test_matricular_returns_404_when_materia_does_not_exist(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})

    response = await client.post("/api/v1/alunos/1/materias/999")

    assert response.status_code == 404


async def test_desmatricular_aluno_returns_204(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/materias", json={"name": "Mat"})
    await client.post("/api/v1/alunos/1/materias/1")

    response = await client.delete("/api/v1/alunos/1/materias/1")

    assert response.status_code == 204


async def test_desmatricular_nao_existente_returns_404(client: AsyncClient) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/materias", json={"name": "Mat"})

    response = await client.delete("/api/v1/alunos/1/materias/1")

    assert response.status_code == 404


async def test_get_aluno_retorna_detail_com_materias_e_notas(
    client: AsyncClient,
) -> None:
    await client.post("/api/v1/alunos", json={"name": "Maria", "email": "m@t.com"})
    await client.post("/api/v1/materias", json={"name": "Matematica"})
    await client.post("/api/v1/alunos/1/materias/1")
    await client.post("/api/v1/notas", json={"aluno_id": 1, "materia_id": 1, "valor": 8})

    response = await client.get("/api/v1/alunos/1")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Maria"
    assert len(body["materias"]) == 1
    assert body["materias"][0]["name"] == "Matematica"
    assert len(body["notas"]) == 1
    assert body["notas"][0]["valor"] == 8
