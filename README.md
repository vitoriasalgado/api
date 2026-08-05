# API — Mentoria

API de estudo para gestão de mentores, alunos, matérias e notas. Feita em FastAPI + SQLAlchemy async como projeto de aprendizado guiado.

## Stack

- **Python 3.12+**
- **FastAPI** — framework web assíncrono
- **Pydantic v2** + **pydantic-settings** — validação e configuração via env
- **SQLAlchemy 2.x** (async) + **aiosqlite** — ORM e driver
- **Alembic** — migrations
- **Uvicorn** — ASGI server
- **Pytest** + **pytest-asyncio** + **httpx** — testes assíncronos
- **Ruff** — lint e formatação (line length 100)
- **uv** — gerenciador de dependências e venv

## Domínio

- **Aluno** — n↔n Matéria (matrícula via `aluno_materia`), 1→n Nota
- **Materia** — n↔n Aluno, 1→n Mentor, 1→n Nota
- **Mentor** — n→1 Materia (FK opcional, `ON DELETE SET NULL`)
- **Nota** — n→1 Aluno + n→1 Materia (`ON DELETE CASCADE`), valor 0–10

## Estrutura

```
api/
├── src/
│   └── app/
│       ├── main.py                  # factory + lifespan + handlers de erro
│       ├── core/
│       │   ├── config.py            # Settings (pydantic-settings)
│       │   ├── exceptions.py        # DomainError, NotFoundError, ConflictError, BusinessRuleError
│       │   ├── error_handlers.py    # tradução domínio → HTTP + resposta padronizada
│       │   └── logging.py           # setup de logging
│       ├── db/
│       │   ├── base.py              # Base declarativa
│       │   └── session.py           # engine + get_db + PRAGMA foreign_keys=ON
│       ├── models/                  # Aluno, Materia, Mentor, Nota + aluno_materia
│       └── api/
│           ├── router.py            # agregador de rotas
│           ├── pagination.py        # Page[T] genérico
│           └── routes/              # health, ping, echo, aluno, materia, mentors, nota
├── alembic/                         # env.py + versions/
├── tests/                           # conftest (fixture in-memory) + test_*.py
├── docs/
│   ├── roadmap.md                   # roadmap do projeto
│   ├── tasks.md                     # backlog de tasks
│   └── conceitos-aprendidos.md      # notas de estudo
├── .env.example
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Setup

Requer Python 3.12+. Recomenda-se [uv](https://docs.astral.sh/uv/).

```bash
# instalar dependências (runtime + dev)
uv sync

# copiar variáveis de ambiente
cp .env.example .env

# aplicar migrations
uv run alembic upgrade head
```

## Rodando

```bash
# dev (hot reload). PYTHONPATH=src é necessário porque uv às vezes
# não mantém o editable install do pacote local warm.
PYTHONPATH=src uv run uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`.

- Docs interativas: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Rotas versionadas sob `/api/v1`

> Em `ENVIRONMENT=production`, `/docs` e `/redoc` ficam desabilitados.

## Endpoints principais

Todos sob `/api/v1`:

- `GET /health`, `GET /ping`, `POST /echo`
- `GET|POST|PATCH|DELETE /alunos[/id]`
- `POST /alunos/{aluno_id}/materias/{materia_id}` — matricular
- `DELETE /alunos/{aluno_id}/materias/{materia_id}` — desmatricular
- `GET /alunos/{aluno_id}/materias` — matérias do aluno
- `GET|POST|PATCH|DELETE /materias[/id]`
- `GET|POST|PATCH|DELETE /mentors[/id]`
- `GET /mentors/{id}/materias`
- `GET|POST|PATCH|DELETE /notas[/id]`

Listagens (`GET /alunos`, `/mentors`, `/materias`, `/notas`) aceitam:

- `skip`, `limit` (paginação, `limit` ≤ 100)
- `sort` (allowlist por rota: `name`, `-name`, `id`, `-id`, etc)
- filtros específicos por rota (`materia_id` em alunos/mentors; `aluno_id` + `materia_id` em notas)

Response envelopado: `{ "items": [...], "total": N, "skip": N, "limit": N }`.

## Erros

Todas as respostas de erro seguem o formato:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Aluno not found",
    "details": { "id": 42 }
  }
}
```

Códigos possíveis: `NOT_FOUND` (404), `CONFLICT` (409), `BUSINESS_RULE_VIOLATION` (422), `VALIDATION_ERROR` (422, payload malformado), `DOMAIN_ERROR` (400 genérico).

## Testes

```bash
uv run pytest                          # suíte inteira
uv run pytest tests/test_nota.py -v    # arquivo único
uv run pytest -k "test_create"         # por nome
```

Cada teste roda contra um SQLite `:memory:` isolado, sem estado compartilhado.

## Lint / format

```bash
uv run ruff check           # report
uv run ruff check --fix     # auto-fix
uv run ruff format          # aplica formatação
```

## Migrations

```bash
uv run alembic revision --autogenerate -m "msg"   # gera a partir do diff dos models
uv run alembic upgrade head                       # aplica
uv run alembic downgrade -1                       # rollback
uv run alembic current                            # head aplicado
```

> SQLite não suporta `ALTER TABLE ADD CONSTRAINT`. Migrations que adicionam FKs a tabelas existentes precisam de `op.batch_alter_table(...)` com constraint **nomeada**. Ver `alembic/versions/8c46aa0e0fc2_add_materia_id_to_mentors.py`.

## Convenções

- **Versionamento**: prefixo `/api/v1` em `main.py`.
- **Rotas**: uma por arquivo em `app/api/routes/`, registradas em `app/api/router.py`. URL plural (`/alunos`), arquivo singular (`aluno.py`).
- **Schemas Pydantic**: `XxxCreate` / `XxxUpdate` (fields opcionais + `model_dump(exclude_unset=True)`) / `XxxRead` (com `from_attributes=True`) próximos da rota.
- **Erros de domínio**: rotas levantam `NotFoundError`, `ConflictError`, `BusinessRuleError` — nunca `HTTPException`. A tradução para HTTP mora em `app/core/error_handlers.py`.
- **Configuração**: tudo via `Settings` em `app/core/config.py`. Nunca ler `os.environ` fora dali.
- **Async por padrão**: handlers, testes e I/O em `async def`.
- **PRAGMA foreign_keys=ON**: registrado no `connect` listener em `app/db/session.py` — SQLite não força FKs por default, várias rotas dependem disso.
