# Tasks — Evoluindo a API para algo robusto

Backlog de tarefas para transformar a base atual (CRUDs de mentor, aluno, matéria, nota em SQLite + Alembic) numa API backend de qualidade profissional.

> **Como usar:** cada task vira **uma branch + um PR pequeno**. Faça na ordem — cada uma depende do contexto da anterior. Antes de abrir o PR, marque o checkbox aqui. Antes de avançar para a próxima, responda mentalmente às "perguntas de verificação".

---

## Fase 1 — Tapar buracos da base (antes de qualquer feature nova)

A base funciona, mas tem 3 buracos que vão fazer dor de cabeça lá na frente. Resolver agora, em PRs pequenos e separados.

### Task 1.1 — Cobertura de testes para aluno, matéria e nota

- [ ] `tests/test_aluno.py`, `tests/test_materia.py`, `tests/test_nota.py`.
- Replicar o padrão de `tests/test_mentors.py`.
- Cobrir, para cada recurso: criar (201), listar, buscar por id, buscar inexistente (404), atualizar (200 + 404), deletar (204 + 404).
- Casos de validação: payload sem campo obrigatório → 422.
- Rodar `uv run pytest` e ver tudo verde.

**Conceitos:** AAA (arrange/act/assert), fixtures de banco isoladas por teste, idempotência de teste.

**Pergunta de verificação:** se dois testes rodam em paralelo e ambos criam um aluno com `email="x@x.com"`, o que acontece? Como o `conftest.py` resolve isso?

---

### Task 1.2 — `relationship()` nos models

Hoje os models só têm `ForeignKey` cru. Sem `relationship()`, você não navega de `Aluno` para `Nota` ou de `Materia` para `Aluno` no código Python — só com query manual.

- [ ] Em `Mentor`: `materia: Mapped["Materia | None"] = relationship(back_populates="mentores")`.
- [ ] Em `Materia`: `mentores`, `alunos` (via `aluno_materia`), `notas`.
- [ ] Em `Aluno`: `materias` (via `aluno_materia`), `notas`.
- [ ] Em `Nota`: `aluno`, `materia`.
- Cada lado com `back_populates` apontando para o outro.
- Imports em `TYPE_CHECKING` para evitar import circular.

**Conceitos:** `relationship`, `back_populates`, `secondary` em many-to-many, lazy loading (e por que ele é problemático em async).

**Pergunta:** o que dá errado se eu acessar `mentor.materia` num handler async sem ter feito eager load?

---

### Task 1.3 — Validar existência antes de criar/atualizar

Hoje dá pra criar uma `Nota` com `aluno_id=999` e o cliente recebe 500 (`IntegrityError` vazando). Inaceitável numa API "completa".

- [ ] Antes do `db.add(...)`, fazer `await db.get(Aluno, aluno_id)` e `Materia` — se não existir, `HTTPException(404, "Aluno not found")`.
- [ ] Regra de negócio em nota: `valor` entre 0 e 10 (validar no schema com `Field(ge=0, le=10)`).
- [ ] Em matrícula (`aluno_materia`): só permite se aluno e matéria existem; matrícula duplicada → 409.
- [ ] `Aluno.email` único: tratar `IntegrityError` na criação → 409 com mensagem clara.
- Testes para cada caso de erro.

**Pergunta:** por que validar no Python se o banco já tem a constraint? (Resposta: UX da API. 422/404/409 explica; 500 não.)

---

## Fase 2 — Endpoints e dados de verdade

### Task 2.1 — Endpoints aninhados com `selectinload`

Cliente quer ver "tudo do aluno" em uma chamada, não 4 requests.

- [ ] `GET /alunos/{id}` retorna `materias` e `notas` aninhadas.
- [ ] `GET /materias/{id}` retorna `mentores` e `alunos`.
- [ ] `GET /mentores/{id}/materias`.
- Schemas separados: `AlunoRead` (raso, para listagens) vs `AlunoDetail` (com aninhamentos).
- Usar `select(Aluno).options(selectinload(Aluno.materias), selectinload(Aluno.notas))`.

**Conceitos:** N+1, `selectinload` vs `joinedload`, response model em camadas.

**Exercício obrigatório:** ligar `echo=True` no engine, fazer a chamada **sem** `selectinload`, contar quantos SQL saem. Depois com `selectinload`, contar de novo. Anotar a diferença.

---

### Task 2.2 — Paginação, filtros e ordenação

Listar 10.000 alunos num GET é receita de timeout.

- [ ] Query params em todos os list endpoints: `skip: int = 0`, `limit: int = Query(50, le=100)`.
- [ ] Response em envelope: `{"items": [...], "total": N, "skip": X, "limit": Y}`.
- [ ] Filtros úteis:
  - `GET /alunos?materia_id=3` — alunos matriculados em uma matéria.
  - `GET /notas?aluno_id=1` e `?materia_id=2`.
  - `GET /mentores?materia_id=3`.
- [ ] Ordenação: `?sort=name` / `?sort=-name` (prefixo `-` = desc).
- Schema genérico `Page[T]` com `Generic[T]`.

**Pergunta:** por que `limit` precisa de um teto máximo? O que acontece se eu deixar o cliente pedir `limit=1000000`?

---

### Task 2.3 — Tratamento centralizado de erros

Parar de espalhar `try/except` pelas rotas.

- [ ] Criar `app/core/exceptions.py` com `DomainError`, `NotFoundError`, `ConflictError`, `BusinessRuleError`.
- [ ] Em `main.py`, registrar `app.add_exception_handler(...)` para cada uma, mapeando para o status HTTP correto.
- [ ] Handler global para `IntegrityError` do SQLAlchemy → 409 com mensagem amigável.
- [ ] Resposta de erro padronizada: `{"error": {"code": "NOT_FOUND", "message": "...", "details": {...}}}`.
- [ ] Refatorar rotas existentes para levantar as exceções de domínio em vez de `HTTPException` direto.

**Conceitos:** exception handlers do FastAPI, separação entre erro de domínio e erro HTTP.

---

## Fase 3 — Infraestrutura de verdade

### Task 3.1 — Docker + docker-compose + Postgres

SQLite é ótimo pra estudar, ruim pra simular produção.

- [ ] `Dockerfile` multi-stage (stage 1: build com `uv sync`; stage 2: runtime `python:3.12-slim` só com o necessário).
- [ ] `docker-compose.yml`:
  - serviço `db`: `postgres:16-alpine`, volume nomeado, `healthcheck` com `pg_isready`.
  - serviço `api`: build local, `depends_on: db: condition: service_healthy`, env `DATABASE_URL`.
- [ ] `.dockerignore` (não copiar `.venv`, `__pycache__`, `.git`, `.pytest_cache`).
- [ ] Trocar `aiosqlite` por `asyncpg` no `pyproject.toml`.
- [ ] Atualizar `.env.example` com URL do Postgres (`postgresql+asyncpg://...`).
- [ ] Migrations rodam **dentro** do container: `docker compose run --rm api uv run alembic upgrade head`.

**Conceitos:** imagem vs container, multi-stage build, volumes nomeados, rede do compose, healthcheck.

**Pergunta:** o que acontece com os dados do banco em `docker compose down`? E em `down -v`?

---

### Task 3.2 — Configuração por ambiente

A `Settings` precisa funcionar em dev, test, e prod sem editar código.

- [ ] `Settings` aceita `DATABASE_URL` separado para `test` (sqlite em memória ou postgres de teste).
- [ ] Em `conftest.py`, forçar `environment=test` e usar um banco isolado (sqlite `:memory:` ou schema separado).
- [ ] Validar settings críticas no startup (`lifespan`): se `environment=production` e `debug=True`, falhar.
- [ ] `.env.example` cobrindo todas as variáveis com comentários.

---

## Fase 4 — Arquitetura

### Task 4.1 — Camadas: repository + service

Os handlers estão fazendo tudo (HTTP + SQL + regra de negócio). Hora de separar — mas sem over-engineering.

Comece pela feature com mais regra: **Nota**.

- [ ] `app/repositories/nota.py` — classe `NotaRepository(session)` com métodos `create`, `get`, `list`, `delete`. Só fala com o banco.
- [ ] `app/services/nota.py` — `NotaService(nota_repo, aluno_repo, materia_repo)` com regra: aluno só ganha nota em matéria onde está matriculado.
- [ ] Rota injeta o service via `Depends`, fica fina: parsing + chamada + response.
- [ ] **Não refatore as outras rotas ainda** — discuta com o mentor antes se vale a pena replicar.

**Conceito chave:** quando vale a pena ter camada e quando ela só polui? Resposta: vale quando há regra de negócio real. CRUD puro pode ficar no handler.

---

## Fase 5 — Segurança

### Task 5.1 — Autenticação com JWT

- [ ] Adicionar `passlib[bcrypt]` e `pyjwt` (ou `python-jose`).
- [ ] Tabela nova `users` com `email` único, `password_hash`, `role` (`mentor` | `aluno` | `admin`) — **não** colocar senha em `Mentor`/`Aluno` diretamente, fazer FK opcional `user_id`.
- [ ] Migration Alembic para `users` + FK.
- [ ] `POST /auth/register` — cria User + perfil (Mentor ou Aluno) numa transação.
- [ ] `POST /auth/login` — valida senha, retorna `{"access_token": "...", "token_type": "bearer"}`.
- [ ] Dependência `get_current_user` que lê `Authorization: Bearer ...`, valida JWT, busca user.
- [ ] Settings novas: `jwt_secret`, `jwt_algorithm`, `jwt_expires_minutes`.

**Conceitos:** hash de senha (nunca texto puro), bcrypt vs argon2, JWT (header.payload.signature), assinatura ≠ criptografia, claim `exp`.

**Pergunta:** se alguém roubar um JWT, o que dá pra fazer pra mitigar? (Discussão: short TTL, refresh token, blocklist.)

---

### Task 5.2 — Autorização por papel (RBAC)

- [ ] Dependência `require_role("mentor")` que rejeita 403 se o user não tem o papel.
- [ ] Aplicar:
  - Criar/atualizar/deletar **matéria** → só `admin`.
  - Lançar **nota** → só `mentor`, e só na matéria que ele dá.
  - Matricular-se em matéria → só o próprio `aluno`.
  - Listar/buscar → autenticado, qualquer papel.
- [ ] Testes cobrindo: papel certo passa, papel errado leva 403, sem token leva 401.

**Pergunta:** diferença entre 401 e 403?

---

