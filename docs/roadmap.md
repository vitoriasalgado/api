# Roadmap de Estudos — API de Mentoria

Este é o **plano de aprendizado** para construir, do zero ao funcional, uma API real em Python. O projeto escolhido é uma **Plataforma de Mentoria** (gerenciar mentores, alunos e sessões) porque os domínios são familiares e permitem evoluir de um CRUD simples até autenticação e relacionamentos.

> **Como usar este documento:** cada módulo é uma etapa. Não pule. Conclua os entregáveis e responda as "perguntas de verificação" antes de avançar. Se travar, volte um passo — é sinal de que um conceito anterior não fechou.

---

## Filosofia

- **Uma coisa de cada vez.** Cada módulo introduz **um** conceito novo sobre o que já existe.
- **Entender > copiar.** O Claude Code pode gerar código em segundos — a sua parte é **explicar o código em voz alta** antes de rodar.
- **Quebrar é bom.** Erros são o material de estudo mais valioso. Leia stack traces, não pule.
- **Commit pequeno e frequente.** Cada passo concluído = um commit. Isso cria histórico pra revisar e ensina disciplina de Git.

---

## Pré-requisitos

Antes de começar, o aluno deve ter:

- Python 3.12+ instalado (`python --version`)
- [uv](https://docs.astral.sh/uv/) instalado (gerenciador de dependências)
- Editor (VS Code recomendado) com extensão Python
- Git configurado (`git config user.name` e `user.email`)
- Conta no GitHub
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado (usaremos a partir do Módulo 7)

---

## Módulo 0 — Fundamentos conceituais (sem código)

**Objetivo:** entender o vocabulário antes de tocar em qualquer arquivo.

### Conceitos

1. **Cliente/Servidor.** O que é um cliente (navegador, curl, app mobile) e o que é um servidor.
2. **HTTP.** O protocolo. Verbos (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), status codes (`2xx`, `4xx`, `5xx`), headers, body.
3. **REST.** Estilo arquitetural — recursos em URLs (`/users/42`), verbos para ações.
4. **JSON.** Formato de troca de dados.
5. **API.** Contrato: quais endpoints existem, o que esperam, o que retornam.
6. **Banco relacional.** Tabelas, colunas, linhas, chaves primárias e estrangeiras.
7. **ORM.** Objeto ↔ Tabela. Por que usar um em vez de escrever SQL cru.
8. **Container / Docker.** Por que empacotar a aplicação junto com o ambiente.

### Entregável

- Um arquivo `docs/glossario.md` (criado pelo aluno) com **uma frase própria** explicando cada termo acima. Sem copiar do Google.

### Perguntas de verificação

- Qual a diferença entre `PUT` e `PATCH`?
- O que significa `404`? E `500`?
- Por que separar frontend de backend via API?

---

## Módulo 1 — Conhecer o projeto base

**Objetivo:** navegar o código existente e rodar a API localmente.

### Passos

1. Clonar o repositório.
2. Rodar `uv sync` — entender o que aconteceu (ler o output).
3. Copiar `.env.example` para `.env`.
4. Rodar `uv run fastapi dev src/app/main.py`.
5. Abrir `http://localhost:8000/docs` no navegador e explorar.
6. Chamar `http://localhost:8000/api/v1/health` pelo navegador **e** pelo terminal com `curl`.
7. Ler, linha por linha, cada arquivo em `src/app/`. Anotar dúvidas.

### Conceitos novos

- `pyproject.toml` e o que é um **lockfile**.
- Variáveis de ambiente (`.env`) e por que não commitá-las.
- **Async/await** (só o suficiente pra reconhecer — não precisa dominar).
- Estrutura `src/` vs. flat layout.

### Entregável

- Aluno consegue explicar, **com as próprias palavras**, o que cada arquivo de `src/app/` faz.
- Commit: nenhum — só exploração.

### Perguntas de verificação

- O que o `create_app()` retorna e por quê?
- O que é `lifespan`? Quando roda?
- Por que `get_settings` e não ler `os.environ` direto?

---

## Módulo 2 — Primeiro endpoint próprio

**Objetivo:** escrever a primeira rota do zero.

### Tarefa

Criar um endpoint `GET /api/v1/ping` que retorna `{"message": "pong"}`.

### Passos

1. Criar `src/app/api/routes/ping.py`.
2. Registrar o router em `src/app/api/router.py`.
3. Testar via `/docs`.
4. Escrever um teste em `tests/test_ping.py` seguindo o padrão de `test_health.py`.
5. Rodar `uv run pytest`.
6. **Commit:** `feat: add ping endpoint`.

### Conceitos novos

- `APIRouter`, `@router.get()`.
- Como o FastAPI gera a documentação automática.
- Teste de integração com `httpx.AsyncClient`.

### Perguntas de verificação

- O que acontece se você esquecer de incluir o router em `router.py`?
- Qual o status code padrão de um `GET`?

---

## Módulo 3 — Pydantic: validação e schemas

**Objetivo:** receber dados do cliente com validação automática.

### Tarefa

Criar `POST /api/v1/echo` que recebe `{"text": "alguma coisa", "repeat": 3}` e retorna `{"result": "alguma coisa alguma coisa alguma coisa"}`.

### Passos

1. Criar um schema `EchoRequest` com `text: str` e `repeat: int` (com validação: 1 ≤ repeat ≤ 10).
2. Criar um schema `EchoResponse`.
3. Escrever o handler.
4. Testar casos inválidos no `/docs` (ex.: `repeat=100`, `text=null`) — observar como o FastAPI responde com `422`.
5. Escrever testes: um caminho feliz, um caso de validação falhando.
6. **Commit:** `feat: add echo endpoint with pydantic validation`.

### Conceitos novos

- `BaseModel`, `Field`, constraints.
- `response_model` no decorator.
- Status `422 Unprocessable Entity`.
- Diferença entre schema de **request** e de **response**.

---

## Módulo 4 — CRUD em memória

**Objetivo:** construir um CRUD completo **antes** de introduzir banco. Isolar o conceito de "verbos REST" do conceito de "persistência".

### Tarefa

Gerenciar **mentores** em memória (uma `dict` global). Endpoints:

- `POST /api/v1/mentors` — cria um mentor (retorna `201` com o objeto criado).
- `GET /api/v1/mentors` — lista todos.
- `GET /api/v1/mentors/{id}` — busca um (retorna `404` se não existe).
- `PATCH /api/v1/mentors/{id}` — atualização parcial.
- `DELETE /api/v1/mentors/{id}` — remove (retorna `204`).

Um mentor tem `id: int`, `name: str`, `expertise: str`, `bio: str | None`.

### Passos

1. Criar `src/app/api/routes/mentors.py`.
2. Criar schemas: `MentorCreate`, `MentorUpdate`, `MentorRead`.
3. Usar uma `dict[int, Mentor]` como "banco" fake.
4. Implementar cada endpoint.
5. Tratar erros com `HTTPException(status_code=404, ...)`.
6. Testes cobrindo cada verbo + casos de erro.
7. **Commit:** `feat: add in-memory mentors CRUD`.

### Conceitos novos

- `HTTPException`.
- `status_code=201` no `POST`, `204` no `DELETE`.
- `Path` parameters vs. `Query` parameters vs. `Body`.
- Por que a dict em memória **não** serve pra produção (race conditions, reset ao reiniciar).

### Perguntas de verificação

- Por que `POST` retorna `201` e não `200`?
- O que acontece com os dados quando você reinicia o servidor?

---

## Módulo 5 — SQLAlchemy + SQLite (persistência)

**Objetivo:** trocar a dict em memória por um banco real. Ainda usando SQLite pra evitar instalar Postgres agora.

### Dependências a adicionar

```
sqlalchemy>=2.0
aiosqlite
```

### Passos

1. Criar `src/app/db/session.py` com o `engine` assíncrono e `async_sessionmaker`.
2. Criar `src/app/db/base.py` com a `Base` declarativa.
3. Criar `src/app/models/mentor.py` com a classe `Mentor` mapeada pra tabela.
4. Criar uma dependência `get_db()` que injeta uma sessão no endpoint.
5. Refatorar as rotas de mentor pra usar a sessão (queries com `select()`).
6. Adicionar no `lifespan` a criação das tabelas (`Base.metadata.create_all` — temporário, até Alembic).
7. Rodar, criar um mentor, **reiniciar o servidor**, listar — e confirmar que persistiu.
8. Ajustar os testes: cada teste deve rodar com um banco limpo (fixture de sessão).
9. **Commit:** `feat: persist mentors in sqlite via sqlalchemy`.

### Conceitos novos

- Engine, sessão, unit of work.
- `Mapped`, `mapped_column`, tipos de coluna.
- `select(...).where(...)`, `session.add`, `await session.commit()`.
- `Depends(get_db)` — injeção de dependência do FastAPI.
- Diferença entre `Mentor` (model ORM) e `MentorRead` (schema Pydantic).

### Armadilhas a discutir

- Não misturar model ORM com schema Pydantic — são coisas diferentes.
- Sempre `await session.commit()`.
- `expire_on_commit=False` em contextos async.

---

## Módulo 6 — Alembic: migrations

**Objetivo:** versionar o schema do banco. Parar de depender de `create_all`.

### Passos

1. Adicionar `alembic` como dependência.
2. Rodar `uv run alembic init -t async alembic`.
3. Ajustar `alembic/env.py` pra importar `Base.metadata` e ler a URL do `Settings`.
4. Remover o `create_all` do `lifespan`.
5. Rodar `uv run alembic revision --autogenerate -m "create mentors table"`.
6. **Ler a migration gerada** antes de aplicar. Sempre.
7. Rodar `uv run alembic upgrade head`.
8. Adicionar uma coluna nova (ex.: `years_of_experience: int`), gerar nova migration, aplicar.
9. Praticar `downgrade` também.
10. **Commit:** `feat: add alembic migrations`.

### Conceitos novos

- Migration como código versionado.
- Autogenerate ≠ infalível (sempre revisar).
- `upgrade` / `downgrade`.
- Por que `create_all` é um anti-pattern em produção.

### Perguntas de verificação

- O que acontece se dois devs gerarem migrations ao mesmo tempo?
- Por que não dá pra simplesmente editar uma migration já aplicada em produção?

---

## Módulo 7 — Docker e docker-compose (Postgres de verdade)

**Objetivo:** rodar API + Postgres em containers. Primeiro contato com infra.

### Entregáveis

- `Dockerfile` multi-stage pra API.
- `docker-compose.yml` com serviços `api` e `db` (Postgres 16).
- `.dockerignore`.

### Passos

1. Escrever o `Dockerfile` (stage 1: build com uv; stage 2: runtime slim).
2. Escrever o `docker-compose.yml`:
   - `db`: imagem `postgres:16-alpine`, volume pra dados, healthcheck.
   - `api`: build local, depende do `db`, env com `DATABASE_URL`.
3. Trocar `aiosqlite` por `asyncpg` nas dependências.
4. Atualizar `.env.example` com a URL do Postgres.
5. Rodar `docker compose up --build`.
6. Entrar no container da API e rodar `alembic upgrade head`.
7. Testar endpoints — funcionando em Postgres.
8. **Commit:** `feat: dockerize api with postgres`.

### Conceitos novos

- Imagem vs. container.
- Multi-stage build (por que separar build de runtime).
- Volumes nomeados (persistência dos dados do Postgres).
- Network interna do compose — `api` fala com `db` pelo nome do serviço.
- Healthcheck e `depends_on: condition: service_healthy`.

### Perguntas de verificação

- O que acontece com os dados do banco se você rodar `docker compose down`? E `down -v`?
- Por que o `.dockerignore` é importante?

---

## Módulo 8 — Relacionamentos e queries

**Objetivo:** modelar o domínio completo e aprender a navegar relações.

### Modelagem

- `Student` (id, name, email).
- `Session` — uma sessão de mentoria (id, mentor_id, student_id, scheduled_at, duration_minutes, notes).
- `Mentor 1-N Session`, `Student 1-N Session`.

### Passos

1. Criar models `Student` e `Session` com `ForeignKey`.
2. Relacionamentos com `relationship()` e `Mapped[list["Session"]]`.
3. Migrations via Alembic.
4. CRUD de `Student`.
5. Endpoint `POST /api/v1/sessions` — validação: mentor e aluno existem, sem conflito de horário.
6. Endpoint `GET /api/v1/mentors/{id}/sessions` — lista sessões de um mentor.
7. Paginação (`skip`, `limit` como query params).
8. Testes cobrindo cada rota e regra de negócio.
9. **Commit:** `feat: add students and mentoring sessions with relationships`.

### Conceitos novos

- Foreign key, lazy loading, `selectinload`.
- Constraints de banco vs. validação na aplicação — onde colocar cada regra.
- Paginação: offset/limit (simples) vs. cursor (discussão conceitual, sem implementar).
- N+1 query problem — mostrar como acontece e como resolver.

---

## Módulo 9 — Autenticação (JWT)

**Objetivo:** proteger endpoints.

### Passos

1. Adicionar `passlib[bcrypt]` e `pyjwt` como dependências.
2. Criar model `User` (mentores e alunos viram `User` com `role`) ou adicionar `password_hash` em `Mentor` — discutir a decisão de modelagem.
3. Endpoint `POST /api/v1/auth/register`.
4. Endpoint `POST /api/v1/auth/login` → retorna `access_token`.
5. Dependência `get_current_user` que lê o header `Authorization: Bearer ...` e valida o JWT.
6. Proteger endpoints que mutam dados.
7. **Commit:** `feat: add jwt authentication`.

### Conceitos novos

- Hash de senha (nunca armazenar em texto puro — explicar por quê).
- Salt, bcrypt, custo computacional.
- JWT: estrutura (header.payload.signature), claims, expiração.
- Por que JWT não é criptografia — é **assinatura**.
- Autenticação vs. autorização (AuthN vs. AuthZ).

### Perguntas de verificação

- Por que não guardar a senha mesmo que em md5?
- O que acontece se alguém roubar um JWT? Como mitigar?

---

## Módulo 10 — Camadas e organização

**Objetivo:** refatorar pra separar responsabilidades. Só depois de ter tudo funcionando — prematuro demais cedo confunde.

### Estrutura alvo

```
src/app/
├── api/routes/       # camada HTTP: recebe request, valida, chama service
├── services/         # regra de negócio (ex.: "não agendar sessão em horário ocupado")
├── repositories/     # acesso a dados (queries SQLAlchemy)
├── models/           # ORM
├── schemas/          # Pydantic
└── core/
```

### Exercício

Escolher uma feature (ex.: agendamento de sessão) e refatorar pra passar pelas três camadas. Discutir: o que melhorou? O que ficou mais verboso?

---

## Módulo 11 — Qualidade e CI (bonus)

**Objetivo:** automatizar o que até agora era manual.

### Tarefas

1. Pre-commit hook rodando `ruff check` e `ruff format --check`.
2. GitHub Actions `.github/workflows/ci.yml`:
   - Instala dependências com uv.
   - Roda `ruff check` + `ruff format --check`.
   - Roda `pytest` contra um Postgres de serviço.
3. Badge de CI no README.

---

## Módulo 12 — Tópicos extras (quando o aluno pedir)

Só introduzir se o aluno mostrar curiosidade — não empilhar:

- **Logging estruturado** com `structlog`.
- **OpenTelemetry** (traces, metrics).
- **Rate limiting** com `slowapi`.
- **Background tasks** (simples: `BackgroundTasks` do FastAPI; avançado: Celery/RQ/Arq).
- **Websockets** (ex.: chat ao vivo entre mentor e aluno).
- **Deploy** (Fly.io, Railway, Render).

---

## Dicas para o mentor (Lucas)

- **Não copie-e-cole do Claude na frente do aluno sem explicar.** A cada geração, pare e pergunte: "o que essa linha faz?".
- **Prefira perguntas a respostas.** "Por que você acha que deu esse erro?" ensina mais do que "o erro é X".
- **Force o aluno a rodar o `/docs` e o `curl`**, não só o teste automatizado. Ver a API de fora é fundamental.
- **Faça ele desenhar.** Antes do Módulo 8, pedir pra ele desenhar no papel as tabelas e os relacionamentos.
- **Comemore os 404.** Quando um teste falha ou um endpoint retorna erro inesperado, é material de aula.

## Dicas para o aluno

- Se entender 60% de um módulo, avance e volte depois — aprendizado não é linear.
- Leia mensagens de erro **completas**. O Python te dá a resposta quase sempre.
- Use o Claude Code, mas **explique o código em voz alta antes de rodar**. Se não consegue explicar, não entendeu ainda.
- Commit pequeno. Mensagem clara. Sempre.
