# API. oi

Base de API em [FastAPI](https://fastapi.tiangolo.com/) com Python 3.12+.

## Stack

- **FastAPI** — framework web assíncrono
- **Pydantic v2** + **pydantic-settings** — validação e configuração via env
- **Uvicorn** — ASGI server
- **Ruff** — lint e formatação
- **Pytest** + **httpx** — testes assíncronos
- **uv** (recomendado) — gerenciador de dependências

## Estrutura

```
api/
├── src/
│   └── app/
│       ├── main.py              # factory da app + lifespan
│       ├── core/
│       │   ├── config.py        # Settings (pydantic-settings)
│       │   └── logging.py       # setup de logging
│       └── api/
│           ├── router.py        # agregador de rotas
│           └── routes/
│               └── health.py    # endpoint de health check
├── tests/
│   ├── conftest.py              # fixtures (AsyncClient)
│   └── test_health.py
├── .env.example
├── pyproject.toml
└── README.md
```

Layout `src/` evita imports acidentais do diretório raiz e é o padrão moderno para pacotes Python.

## Setup

Requer Python 3.12+. Recomenda-se [uv](https://docs.astral.sh/uv/).

```bash
# instalar dependências (runtime + dev)
uv sync

# copiar variáveis de ambiente
cp .env.example .env
```

Alternativa sem uv:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Rodando

```bash
# dev (hot reload)
uv run fastapi dev src/app/main.py

# produção
uv run fastapi run src/app/main.py
```

A API sobe em `http://localhost:8000`.

- Docs interativas: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health check: `http://localhost:8000/api/v1/health`

> Em `ENVIRONMENT=production` o `/docs` e `/redoc` ficam desabilitados.

## Testes

```bash
uv run pytest
```

## Lint / format

```bash
uv run ruff check .
uv run ruff format .
```

## Convenções

- **Versionamento de rotas**: prefixo `/api/v1` em `main.py`. Novas versões ficam em `/api/v2`, etc.
- **Rotas**: uma por arquivo em `app/api/routes/`, registradas em `app/api/router.py`.
- **Configuração**: tudo via `Settings` em `app/core/config.py`, lido do `.env`. Nunca acessar `os.environ` fora dali.
- **Async por padrão**: handlers, testes e I/O em `async def`.
- **Schemas**: modelos Pydantic de request/response próximos da rota que os usa; promover para `app/schemas/` quando reutilizados.

## Próximos passos sugeridos

Quando a API crescer, considerar adicionar:

- **Banco de dados**: SQLAlchemy 2.x (async) + Alembic para migrations
- **Autenticação**: dependência de `Security` com JWT ou OAuth2
- **Camada de domínio**: separar `services/` (regra de negócio) de `repositories/` (persistência)
- **Observabilidade**: OpenTelemetry (traces/metrics) e structured logging (structlog)
- **Container**: `Dockerfile` multi-stage
- **CI**: GitHub Actions rodando `ruff check`, `ruff format --check` e `pytest`
