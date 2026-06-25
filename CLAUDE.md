# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context: a learning project

This is a teaching repository following the staged roadmap in `docs/roadmap.md`. The user is learning FastAPI/SQLAlchemy/Alembic step by step and works alone (no external mentor). The current backlog of evolution tasks lives in `docs/tasks.md` (Task 1.1 → 5.2).

**Learning mode is strict:** explain *what* and *why*, the user writes the code, you review afterwards. Do not write code *for* her even when asked to "verify" or "fix" — point at the file/line and the rule, let her edit. See `memory/feedback_guided_learning.md`.

## Tech stack

- **Python 3.12+**, package + venv managed by `uv`
- **FastAPI** (async) + **Pydantic v2** for HTTP layer
- **SQLAlchemy 2.x async** (`AsyncSession`, `Mapped`, `mapped_column`) + **aiosqlite**
- **Alembic** for migrations (autogenerate-driven, manual fixups for SQLite FK ALTER)
- **pytest** + **pytest-asyncio** (`asyncio_mode="auto"`) + **httpx.AsyncClient** for tests
- **ruff** for lint + format (line length 100)
- **SQLite** as the only DB (single-file dev, `:memory:` for tests)

## Workflow

- **Branch per task**: `task-X.Y-<slug>` (or `modulo-X-<slug>` for old roadmap modules)
- Local commits on the branch, **conventional commit prefixes** (`feat:`, `fix:`, `test:`, `chore:`, `docs:`, `refactor:`)
- Push to `origin` for backup/history, but **no PRs and no remote review** — user merges locally
- After merging into `main`: pull, delete local branch, delete remote branch
- The user still does the **"Perguntas de verificação"** from `docs/tasks.md` as a learning exercise at the end of each task — she answers herself, then asks for review

## Safety / don'ts

- **Don't bulk-implement.** Work one file/concept at a time. If she asks for 4 CRUDs, propose the order and wait for "go" on each.
- **Don't write code for her.** Explain the *what* (which file, which lines, which functions) and the *why* (the concept, the trade-off). She writes; you review.
- **Don't pre-fill "Perguntas de verificação" answers.** Leave the questions, remind her to answer, then comment/refine her answers — never substitute them. See `memory/feedback_verification_questions.md`.
- **Don't run commands she should run.** Hand her the command, let her run it, ask for output if needed. Exceptions: `Read`/`Bash` for inspection.
- **Don't restructure files unprompted.** This is a learning codebase — surprise refactors break her mental model.

## Commands

```bash
# install deps (runtime + dev)
uv sync

# dev server (hot reload). NOTE: uv run sometimes drops the editable install of the
# local `app` package, so PYTHONPATH=src is the safe form
PYTHONPATH=src uv run uvicorn app.main:app --reload

# tests
uv run pytest                          # full suite
uv run pytest tests/test_nota.py -v    # single file
uv run pytest -k "test_create"         # by name pattern

# lint + format
uv run ruff check                      # report
uv run ruff check --fix                # auto-fix what's fixable
uv run ruff format                     # apply formatting

# alembic
uv run alembic revision --autogenerate -m "msg"   # generate migration from model diff
uv run alembic upgrade head                       # apply
uv run alembic downgrade -1                       # rollback one step
uv run alembic current                            # show applied head
```

API runs at `http://localhost:8000`, docs at `/docs`, all routes under `/api/v1`.

## Architecture

**`src/` layout with hatchling.** `pyproject.toml` declares `packages = ["src/app"]` and `[tool.pytest.ini_options] pythonpath = ["src"]`. The Alembic config also has `prepend_sys_path = src` for the same reason. Anything that imports `app.*` outside pytest/alembic usually needs `PYTHONPATH=src` because `uv run` doesn't always keep the editable install warm.

**App factory + lifespan.** `app/main.py:create_app()` builds the FastAPI instance, mounts CORS conditionally on `settings.cors_origins_list`, and includes `api_router` under `/api/v1`. `lifespan` only sets up logging now — schema creation moved to Alembic (no more `Base.metadata.create_all`).

**Routes are flat and feature-scoped.** Each file in `app/api/routes/` owns one resource (Pydantic schemas + handlers in the same file) and exposes a `router` registered in `app/api/router.py`. Pattern per resource: `XxxCreate` (all required), `XxxUpdate` (all optional, used with `model_dump(exclude_unset=True)`), `XxxRead` (with `ConfigDict(from_attributes=True)`). The DI alias `DbSession = Annotated[AsyncSession, Depends(get_db)]` is repeated locally in each route file.

**DB layer.** `app/db/session.py` builds an async engine from `settings.database_url` and registers a SQLAlchemy `connect` listener that issues `PRAGMA foreign_keys=ON`. **This is load-bearing** — SQLite doesn't enforce FKs by default, and several routes (notably `nota`) depend on `IntegrityError → 409` translation. The same PRAGMA listener is duplicated in `tests/conftest.py` because the test fixture creates its own in-memory engine; if you touch one, touch the other.

**Models register via `app/models/__init__.py`.** Alembic's `env.py` does `import app.models` so any new model must be re-exported there for `--autogenerate` to see it. The `aluno_materia` association is a bare `Table`, not a class, and is also exported.

**Domain shape:** mentor n→1 materia (FK on mentor with `ondelete=SET NULL`); aluno n↔n materia (association `aluno_materia`, composite PK, `CASCADE`); nota n→1 aluno + n→1 materia (`CASCADE`). Nota validates `valor` 0–10 at the Pydantic layer, and translates FK `IntegrityError` to 409.

**SQLite + Alembic gotcha.** SQLite doesn't support `ALTER TABLE ADD CONSTRAINT`. Migrations that add FKs to existing tables must use `op.batch_alter_table(...)` with a **named** constraint (so the matching `drop_constraint` works). See `alembic/versions/8c46aa0e0fc2_add_materia_id_to_mentors.py` for the canonical example.

**Settings.** `app/core/config.py` — single `Settings(BaseSettings)` reading `.env`, cached via `@lru_cache`. Never read `os.environ` outside this module. `is_production` toggles `/docs` and `/redoc` off.

## Testing

- `tests/conftest.py` provides two fixtures: `db_session` creates a fresh `sqlite+aiosqlite:///:memory:` per test (full isolation, no shared state, no parallel-write issues), and `client` overrides `get_db` to inject it into an `httpx.AsyncClient` against the ASGI app.
- `pytest.ini_options` sets `asyncio_mode = "auto"`, so test functions don't need `@pytest.mark.asyncio`.
- Helper functions inside a test module are conventionally prefixed `_` (e.g. `_seed_aluno_e_materia` in `test_nota.py`).
- **Quality bar:** every new route/handler needs at least the happy path + the 404/409/validation edge cases that handler can raise. Ruff (`check` + `format`) must pass before commit.

## Conventions worth knowing

- Inside `except` clauses, `raise HTTPException(...) from None` (rule B904). The `from None` is intentional: we translate domain errors to HTTP, we don't chain stack traces to the client.
- Line length is **100** (`pyproject.toml`). Long `raise` lines that exceed it must be broken across multiple lines, not silenced.
- Route paths use the resource singular folder name but the URL is plural (`routes/materia.py` → `/materias`). The router import name matches the file name.
