# Pull Requests — Guia do Mentorado e Fluxo de Aprovação

Este documento define **como o mentorado deve submeter Pull Requests (PRs) por módulo concluído** do [roadmap](./roadmap.md), e **como o mentor vai revisar e aprovar** cada entrega.

> **Resumo em uma linha:** cada módulo do roadmap vira **uma branch** → **um PR** → **uma revisão** → **um merge**. Sem atalhos.

---

## 1. O que é um Pull Request

Um **Pull Request** (PR) é um pedido formal para incorporar o código de uma branch em outra (geralmente `main`). Ele existe pra três coisas:

1. **Revisão.** Outra pessoa lê seu código antes dele virar "oficial".
2. **Discussão.** Comentários linha a linha criam um registro do "por quê" das decisões.
3. **Portão de qualidade.** CI (lint, testes) roda automaticamente antes do merge.

Um PR **não** é um botão de "enviar tarefa". É uma **conversa** sobre um conjunto de mudanças.

### Vocabulário mínimo

- **Branch** — linha de desenvolvimento paralela. `main` é a principal.
- **Commit** — uma unidade atômica de mudança, com mensagem explicando o porquê.
- **Base branch** — onde o PR vai ser mergeado (aqui, sempre `main`).
- **Head branch** — a branch com suas mudanças (ex.: `modulo-2-ping-endpoint`).
- **Diff** — o que mudou: linhas adicionadas (verde) e removidas (vermelho).
- **Review** — parecer do revisor: `Approve`, `Request changes` ou `Comment`.
- **Merge** — ato de incorporar a branch na base. Feito só após aprovação.

---

## 2. Quando abrir um PR

**Um PR por módulo concluído.** Nem mais, nem menos.

- ✅ Terminou o Módulo 2 (ping endpoint)? Abra um PR.
- ✅ Terminou o Módulo 4 (CRUD em memória)? Abra outro PR.
- ❌ Não junte dois módulos em um PR só — perde o valor didático da revisão isolada.
- ❌ Não abra PR com código pela metade (ex.: testes faltando, endpoint sem validação).

### Critérios para considerar um módulo "pronto pra PR"

Antes de abrir o PR, confirme **todos** os itens abaixo:

- [ ] Todos os **entregáveis** do módulo estão implementados.
- [ ] Os **testes novos passam** localmente: `uv run pytest`.
- [ ] Os **testes antigos continuam passando** (nada foi quebrado).
- [ ] O **lint está limpo**: `uv run ruff check` e `uv run ruff format --check`.
- [ ] Você consegue **explicar em voz alta** o que cada linha do seu diff faz.
- [ ] Você respondeu mentalmente as **perguntas de verificação** do módulo.

Se qualquer item acima falha, **não abra o PR ainda**. Abrir PR incompleto só pra "mostrar progresso" polui o histórico de revisão.

---

## 3. Fluxo do mentorado — passo a passo

### 3.1. Antes de começar o módulo

Garanta que sua `main` local está atualizada:

```bash
git checkout main
git pull origin main
```

Crie uma branch nova pro módulo. **Use o padrão de nome:**

```
modulo-<número>-<descrição-curta-em-kebab-case>
```

Exemplos:
- `modulo-2-ping-endpoint`
- `modulo-4-mentors-crud`
- `modulo-5-sqlalchemy-sqlite`

```bash
git checkout -b modulo-2-ping-endpoint
```

### 3.2. Durante o módulo — commits pequenos

Siga a regra do roadmap: **cada passo concluído = um commit**. Isso:

- Facilita revisar passo a passo.
- Permite desfazer um erro sem perder tudo.
- Ensina disciplina de Git.

**Formato de mensagem** (convencional):

```
<tipo>: <descrição curta no imperativo>

[corpo opcional explicando o porquê, não o quê]
```

Tipos comuns:
- `feat` — nova funcionalidade
- `fix` — correção de bug
- `test` — adição/ajuste de testes
- `refactor` — mudança de código sem alterar comportamento
- `docs` — só documentação
- `chore` — tarefas de manutenção (deps, config)

Exemplos:
```
feat: add ping endpoint
test: cover ping endpoint happy path
refactor: extract mentor repository from route
```

### 3.3. Antes de abrir o PR — checklist local

```bash
# 1. Testes passando
uv run pytest

# 2. Lint limpo
uv run ruff check
uv run ruff format --check

# 3. Ver o que vai no PR
git log main..HEAD --oneline
git diff main...HEAD
```

Leia o próprio diff **antes** de abrir o PR. Se tem coisa que você não explica, não está pronto.

### 3.4. Subir a branch e abrir o PR

```bash
git push -u origin modulo-2-ping-endpoint
```

O GitHub vai sugerir um link pra abrir o PR. Use-o, ou abra manualmente na interface.

### 3.5. Descrição do PR — template obrigatório

Use **sempre** este template na descrição:

```markdown
## Módulo
Módulo X — <título do módulo no roadmap>

## O que foi feito
- <item 1>
- <item 2>
- <item 3>

## Como testar
1. `uv sync`
2. `uv run fastapi dev src/app/main.py`
3. `curl http://localhost:8000/api/v1/...`

## Perguntas de verificação (respostas)
- **<pergunta 1 do roadmap>?** <sua resposta>
- **<pergunta 2 do roadmap>?** <sua resposta>

## Dúvidas / pontos pra discutir
- <dúvida 1, se houver>
- <ponto em que você ficou inseguro, se houver>

## Checklist
- [x] Testes passando localmente
- [x] Ruff check + format limpos
- [x] Li meu próprio diff
- [x] Consigo explicar cada linha
```

**A seção "Dúvidas / pontos pra discutir" é a mais importante.** É ali que a mentoria acontece. Seja honesto: "copiei do Claude e não entendi direito essa parte" é uma entrada válida — e muito mais útil do que fingir que entendeu.

### 3.6. Título do PR

Siga o mesmo padrão dos commits, prefixado com o módulo:

```
[Módulo 2] feat: add ping endpoint
[Módulo 4] feat: add in-memory mentors CRUD
[Módulo 5] feat: persist mentors in sqlite via sqlalchemy
```

---

## 4. Fluxo do mentor — revisão e aprovação

O mentor (Lucas) segue este fluxo **sempre**, pra manter consistência e não pular etapas.

### 4.1. Acusar recebimento (até 24h)

Assim que o PR aparece, o mentor:

1. Lê título e descrição.
2. Comenta no PR reconhecendo o recebimento e dando prazo estimado de revisão.
   > Ex.: *"Recebido — revisão até sexta. Qualquer urgência, me chama."*

Isso evita que o mentorado fique no limbo.

### 4.2. Primeira passada — leitura a frio

O mentor abre a aba **Files changed** e lê o diff **sem rodar o código**, perguntando-se:

- O código **resolve** o que o módulo pede?
- A estrutura segue o que já existe no repo?
- Tem teste cobrindo o caminho feliz e pelo menos um caso de erro?
- Algum nome de variável/função está confuso?
- Tem código morto, comentário sobrando, print esquecido?

Anotações viram **comentários inline** no PR.

### 4.3. Segunda passada — rodando localmente

```bash
git fetch origin
git checkout modulo-2-ping-endpoint
uv sync
uv run pytest
uv run fastapi dev src/app/main.py
# testa o endpoint via /docs e curl
```

Valida:

- Testes realmente passam.
- Endpoint funciona de ponta a ponta.
- Casos de borda (dados inválidos, IDs inexistentes) retornam o status correto.

### 4.4. Tipos de comentário

O mentor classifica cada comentário com um prefixo, pra deixar claro o peso:

- **`[bloqueador]`** — precisa ser resolvido antes do merge. Ex.: bug, teste faltando, segurança.
- **`[sugestão]`** — melhoria recomendada, mas opcional. Ex.: renomear variável, extrair função.
- **`[nit]`** — detalhe estético (picuinha). Ex.: espaço em branco, ordem de imports.
- **`[pergunta]`** — o mentor quer entender o raciocínio antes de opinar.
- **`[didático]`** — explicação pra fixar um conceito. Não exige mudança, mas exige leitura.

O mentorado **deve responder a todos os comentários** — nem que seja com um "ok, entendi" ou "vou deixar assim porque X".

### 4.5. Decisão da review

O mentor usa o botão de review do GitHub com uma das três opções:

- **`Approve`** — tudo certo, pode mergear. Usado quando não há `[bloqueador]`.
- **`Request changes`** — há pelo menos um `[bloqueador]`. Mentorado precisa corrigir e pedir nova review.
- **`Comment`** — revisão parcial (ex.: primeira passada, sem rodar ainda). Não aprova nem bloqueia.

### 4.6. Ciclo de correção

Se veio `Request changes`:

1. Mentorado resolve cada `[bloqueador]`, commita e dá push na mesma branch.
   - **Não force-push** durante revisão (quebra o histórico de comentários).
2. Mentorado responde cada thread com `Done` + link do commit, ou com a justificativa.
3. Mentorado clica em **Re-request review**.
4. Mentor revisa só o delta e decide de novo.

O ciclo pode acontecer várias vezes. Isso **não é problema** — é o coração do aprendizado.

### 4.7. Aprovação e merge

Quando o PR é aprovado:

- **Quem mergeia:** o mentorado (pra ele exercitar o fluxo completo).
- **Tipo de merge:** `Squash and merge` (recomendado) — junta todos os commits do módulo em um só na `main`, mantendo o histórico limpo.
- **Mensagem do squash:** o título do PR.
- Após o merge, **deletar a branch remota** (botão que aparece no GitHub).
- Localmente:
  ```bash
  git checkout main
  git pull origin main
  git branch -d modulo-2-ping-endpoint
  ```

Só depois disso, o próximo módulo começa.

---

## 5. Regras inegociáveis

- **Nunca commit em `main` diretamente.** Sempre via PR.
- **Nunca merge sem review aprovada.** Mesmo se "é só uma linha".
- **Nunca force-push em branch que já está em review** (reescreve histórico e confunde o revisor).
- **Nunca feche um PR sem explicar** por quê. Se o trabalho foi abandonado, comente o motivo.
- **Nunca ignore um `[bloqueador]`.** Ou resolve, ou discute e chega num acordo registrado.

---

## 6. Perguntas frequentes

**E se eu descobrir um bug numa coisa já mergeada?**
Abre um PR novo com prefixo `fix:` — ex.: `[Fix Módulo 4] fix: return 404 when mentor id is negative`. Não reabre PR antigo.

**E se o mentor demorar pra revisar?**
Dá um nudge depois de 48h. O mentor é humano, esquece.

**Posso abrir um PR "rascunho" pra pedir ajuda antes de terminar?**
Pode — use o botão **Draft pull request** do GitHub. Deixe claro na descrição que é rascunho e o que especificamente você quer discutir. Só não marque como "ready for review" antes de cumprir o checklist da seção 3.3.

**E se eu travar no meio de um módulo?**
Pausa, abre uma issue ou manda mensagem. Não force a barra — o roadmap diz: *"se travar, volte um passo"*.

**Posso usar Claude Code pra escrever o código?**
Sim, mas com a regra do roadmap: **explique cada linha em voz alta antes de rodar**. No PR, se tem trecho que você não entende 100%, marca em `Dúvidas / pontos pra discutir`. Honestidade > aparência.

---

## 7. Referência rápida — comandos Git do fluxo

```bash
# Início do módulo
git checkout main
git pull origin main
git checkout -b modulo-X-descricao

# Durante o módulo (repetir a cada passo)
git add <arquivos>
git commit -m "tipo: descrição"

# Antes do PR
uv run pytest
uv run ruff check
uv run ruff format --check
git log main..HEAD --oneline
git diff main...HEAD

# Subir
git push -u origin modulo-X-descricao

# Depois do merge
git checkout main
git pull origin main
git branch -d modulo-X-descricao
```

---

**Este documento é vivo.** Se algo no fluxo não estiver funcionando, comenta com o mentor e a gente ajusta aqui mesmo — via PR, claro.
