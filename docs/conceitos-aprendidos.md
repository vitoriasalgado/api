# Conceitos aprendidos

Compilação de conceitos que apareceram durante o desenvolvimento do projeto, organizados por área.

---

## Python básico

### `return` encerra a função

Assim que Python encontra um `return`, a função termina. Qualquer código depois dele **nunca executa** — é "dead code".

```python
def f(x):
    return "sim"
    print("nunca sai")   # <- inalcançável
```

### Atribuição é dinâmica

Uma variável em Python não tem tipo fixo. `x = 10` (int), depois `x = "dez"` (str) — Python aceita. A responsabilidade de "essa variável guarda o quê" é sua. Cuidado com sobrescrever uma FK (`int`) com um objeto ORM: a comparação seguinte compara **o objeto**, não o id.

### Referência vs valor

Com objetos **mutáveis** (list, dict, set), `b = a` **compartilha** o objeto — não copia.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)   # [1, 2, 3, 4]
```

Pra copiar de verdade: `b = a.copy()` ou `b = list(a)`.

### Indentação

Corpo de função precisa estar indentado (4 espaços) em relação ao `def`. Misturar níveis dá `IndentationError`.

### Métodos de lista

- **`.append(x)`** — adiciona `x` no fim da lista. `[1, 2].append(3)` → `[1, 2, 3]`.
- **`.pop()`** — remove e retorna o último.
- **`.copy()`** — cria cópia rasa (evita compartilhamento por referência).
- **`len(lista)`** — quantidade de elementos.

### `dict` vs `list` — como acessar

- **Lista** → indexa por posição: `body[0]`, `body[1]`.
- **Dict** → indexa por chave: `body["id"]`, `body["materias"]`.

Confundir dá `TypeError` ou `KeyError`. Response JSON com `{...}` = dict. Response com `[...]` = lista.

```python
# GET /alunos/1  →  { "id": 1, "name": "Maria", "materias": [...] }  (dict)
body["materias"]        # ✓ acessa por chave
body[0]                 # ✗ TypeError

# GET /alunos    →  [ { "id": 1 }, { "id": 2 } ]  (lista de dicts)
body[0]                 # ✓ primeiro elemento
body[0]["name"]         # ✓ nome do primeiro
```

### Strings precisam de aspas

`Matematica` (sem aspas) é uma **variável**. `"Matematica"` (com aspas) é uma **string literal**. Esquecer as aspas dá `NameError` (Python procura uma variável chamada `Matematica`).

---

## Async / await

### Por que existe

Servidor síncrono **congela** enquanto espera IO (banco, rede). Async permite soltar a vez e atender outra request enquanto espera.

### Regras práticas

- Função que faz IO é `async def`
- Chama função async com `await`
- Toda função que usa `await` precisa ser `async def` (contamina pra cima)

Esqueceu o `await`? Recebe uma promessa (`coroutine object`), não o valor. Bug silencioso.

### `MissingGreenlet`

Erro clássico em SQLAlchemy async: você tenta acessar uma relação (`aluno.materias`) que **não foi pré-carregada**. O lazy load tenta rodar SQL fora de um `await` — async não permite. Solução: pré-carregar com `selectinload` no `select`.

---

## FastAPI

### `Query()` — validar query params

```python
skip: int = Query(0, ge=0)
limit: int = Query(50, ge=1, le=100)
```

- `ge` = greater or equal (mínimo)
- `le` = less or equal (máximo)
- Cliente pedindo valor inválido → HTTP 422 automático

### Status codes

- **200 OK** — GET com corpo (default do FastAPI)
- **201 Created** — POST bem-sucedido
- **204 No Content** — DELETE (sem corpo na resposta)
- **404 Not Found** — recurso não existe
- **409 Conflict** — violação de constraint (ex: email duplicado)
- **422 Unprocessable Entity** — validação Pydantic falhou

### Lista vazia ≠ 404

`GET /mentors/1/materias` onde o mentor 1 existe mas não tem matéria → **200 com `[]`**, não 404. 404 é pro caso do mentor não existir.

---

## Pydantic

### Papel

Validação e serialização **no boundary HTTP** (entrada + saída). Traduz JSON ↔ Python.

Não é "regras do ambiente" — é regra **do que entra e sai da API**. Dentro da aplicação (modelos ORM, lógica), Pydantic não interfere. Ele age só no momento em que dados atravessam a fronteira: request chegando (JSON → objeto validado) e response saindo (objeto → JSON).

### Onde importar

- `BaseModel`, `ConfigDict`, `Field` → `from pydantic import ...`
- **`EmailStr`** → `from pydantic import EmailStr` (validador especializado de email)
- `BaseSettings` → `from pydantic_settings import BaseSettings` (pacote separado)

### Schemas em camadas

- `XxxCreate` — todos os campos obrigatórios (POST)
- `XxxUpdate` — todos opcionais, usado com `.model_dump(exclude_unset=True)` (PATCH)
- `XxxRead` — resposta rasa (listagens)
- `XxxDetailRead` — resposta com relações aninhadas (GET by id)

**Por que separar Read e DetailRead?**
- Payload menor em listagem (imagina 100 alunos × 10 matérias × 20 notas)
- Menos queries no banco (não faz eager load se não precisa)
- Contrato de API mais claro

### `ConfigDict(from_attributes=True)`

Necessário quando o schema vai ser populado a partir de um **objeto ORM** (não dict). Sem isso, Pydantic não sabe ler atributos do objeto.

### Nome de campo do schema = nome da relação no modelo

Se o modelo `Materia` tem `mentores: Mapped[list[Mentor]]` (português, plural), o schema também precisa ser `mentores: list[MentorNested]`. Se você escrever `mentors`, Pydantic devolve lista vazia sem reclamar.

---

## SQLAlchemy

### Query

"Query" = **consulta**. É a pergunta/instrução que a aplicação faz ao banco de dados. `SELECT * FROM alunos` é uma query. No SQLAlchemy, você constrói queries em Python (`select(Aluno).where(...)`) e o SQLAlchemy traduz pra SQL na hora de executar.

Termos relacionados:
- **Query** = pergunta ao banco (SELECT em 90% dos casos)
- **Statement** = qualquer instrução SQL (SELECT, INSERT, UPDATE, DELETE)
- **Stmt** (`stmt`) = variável convencional pra guardar uma statement

### `stmt` (statement)

Variável convencional pra guardar uma query montada mas ainda não executada. Abreviação de "SQL statement" (instrução SQL).

```python
stmt = select(Aluno).where(Aluno.id == 1)
result = await db.execute(stmt)
```

**Nada vai ao banco até `db.execute(stmt)`.** Até lá, `stmt` é só um objeto Python descrevendo a query. Isso permite montar a query passo a passo, condicionalmente:

```python
stmt = select(Aluno)                          # base
if filtro_materia:
    stmt = stmt.join(...).where(...)          # anexa se precisar
if ordenar:
    stmt = stmt.order_by(Aluno.name)          # anexa se precisar
result = await db.execute(stmt.offset(0).limit(10))   # execução única
```

Cada método (`.where`, `.join`, `.order_by`, `.offset`, `.limit`) retorna um **novo stmt** com a cláusula anexada — não modifica o original. É por isso que a atribuição `stmt = stmt.join(...)` é necessária.

### Convenções de nome

- **`stmt`** — genérico, funciona pra SELECT/INSERT/UPDATE/DELETE
- **`query`** — também comum, especialmente pra SELECT
- **`q`** — quando o escopo é pequeno

Pode chamar do que quiser — SQLAlchemy não se importa. `stmt` é convenção da comunidade.

### Composição condicional

O poder do `stmt` está em construir a query **em partes**:

```python
stmt = select(Aluno)

if materia_id is not None:
    stmt = stmt.join(aluno_materia).where(aluno_materia.c.materia_id == materia_id)

if sort == "name":
    stmt = stmt.order_by(Aluno.name)
elif sort == "-name":
    stmt = stmt.order_by(Aluno.name.desc())

count = await db.execute(select(func.count()).select_from(stmt.subquery()))
items = await db.execute(stmt.offset(skip).limit(limit))
```

Mesmo `stmt` reusado em duas execuções distintas. **Imutável no sentido de que cada operação retorna novo objeto** — mas você pode reassignar à mesma variável.

### `db.get(Model, pk)` vs `db.execute(select(...))`

- **`db.get(Model, pk)`** — busca por chave primária. Retorna o objeto ou `None`. Sintaxe curta pra caso comum.
- **`db.execute(select(...))`** — busca com filtros complexos, joins, options (selectinload). Mais poderoso, mais verboso.

### `scalar_one_or_none()` vs `.scalars().all()`

- **`scalar_one_or_none()`** — espera 0 ou 1 resultado. Retorna o objeto ou `None`.
- **`.scalars().all()`** — retorna todos os resultados como lista.

### N+1

Quando você faz 1 query pra pegar N itens, e depois N queries adicionais pra carregar uma relação de cada. Total = 1 + N.

Exemplo: `GET /alunos` retorna 20 alunos. Sem eager load, cada acesso a `aluno.notas` dispara 1 query nova → 1 + 20 = **21 queries**.

### `selectinload` vs `joinedload`

Ambos evitam N+1, com estratégias diferentes:

- **`joinedload`** — usa JOIN. 1 query só, mas duplica linhas do "pai" pra cada filho.
- **`selectinload`** — usa `WHERE ... IN (...)`. Mais queries (1 por relação), sem duplicação.

Regra prática:
- Relação N-para-1 (aluno → 1 escola) → `joinedload`
- Relação 1-para-muitos ou N-para-N (aluno → várias notas) → `selectinload`

### `func.count()` — contar total no banco

```python
select(func.count()).select_from(Aluno)
```

Retorna o número de linhas. Executa como `SELECT count(*) FROM alunos`.

### `stmt.subquery()` — contar sobre stmt filtrado

Quando quer o count de uma query já filtrada:

```python
stmt = select(Aluno).join(...).where(...)
count = select(func.count()).select_from(stmt.subquery())
```

Gera SQL tipo `SELECT count(*) FROM (SELECT * FROM ... WHERE ...)`.

### Tabela associativa (`Table`, não classe)

`aluno_materia` é uma `Table` (não classe), porque não tem atributos além das FKs. Acesso a colunas: `aluno_materia.c.aluno_id` — o `.c` é o "columns" da Table.

### PRAGMA foreign_keys=ON

SQLite **não enforça FKs por default**. O projeto tem um event listener em `db/session.py` que dispara `PRAGMA foreign_keys=ON` a cada conexão. Sem isso, FK violation não vira `IntegrityError` — vira dado corrompido.

---

## Paginação e filtros

### `Generic[T]`

Permite criar **uma classe** que funciona pra qualquer tipo:

```python
T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
```

Depois usa como `Page[AlunoRead]`, `Page[MateriaRead]`, etc. `T` é um "placeholder de tipo" — decidido no uso.

### `skip` + `limit`

Estilo de paginação alinhado ao SQL:

- `.offset(skip)` — pula N linhas
- `.limit(limit)` — pega até M linhas

Alternativa comum: `page` + `size` (mais amigável, mais matemática interna).

### Filtro afeta count E items

Se você filtra os items mas conta tudo, o `total` fica errado. **Monta o stmt base com filtro uma vez, deriva as duas queries dele.**

### Teto no `limit`

`Query(50, ge=1, le=100)` — cliente **não pode** pedir `limit=1000000`. Sem teto, servidor faz query gigante e trava.

---

## Testes

### Fixtures do `conftest.py`

- **`db_session`** — banco SQLite em memória (`:memory:`), novo a cada teste. Isolado.
- **`client`** — `httpx.AsyncClient` apontando pra app. **Redirecionado** pro `db_session` do teste via `dependency_overrides[get_db]`. Setup e action compartilham o mesmo banco.

### Estrutura de um teste

```python
async def test_xxx(client, db_session):
    # 1. Setup — cria dados (via client.post OU db_session.add)
    # 2. Action — client.get/post/... (a chamada que está sendo testada)
    # 3. Assertions — checa status + corpo
```

### Cobertura mínima

Cada handler novo → **happy path + edge cases** (404, 409, 422). Ruff (`check` + `format`) precisa passar antes de commit.

---

## Alembic (migrations)

### Autogenerate

`alembic revision --autogenerate -m "msg"` compara os modelos com o estado atual do banco e gera diff.

### SQLite + ADD CONSTRAINT

SQLite **não suporta** `ALTER TABLE ADD CONSTRAINT`. Migrations que adicionam FK a tabela existente precisam usar `op.batch_alter_table(...)` com constraint **nomeada** (para o `drop_constraint` funcionar).

---

## Workflow git (solo)

- Branch por task: `task-X.Y-<slug>`
- Commits locais com prefixo convencional: `feat:`, `fix:`, `test:`, `chore:`, `docs:`, `refactor:`
- Push pra origin como backup
- Merge local em `main`, sem PR
- Pós-merge: `git branch -d` local + `git push origin --delete` remoto