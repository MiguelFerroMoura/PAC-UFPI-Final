# Correção de Conexão com o Banco de Dados

Documentação técnica sobre os erros de conexão com o PostgreSQL encontrados durante a configuração do ambiente local, as decisões tomadas e as implementações realizadas.

---

## Contexto

Durante a geração das migrations iniciais do projeto (`python manage.py makemigrations`), o comando falhou com um erro de codificação antes mesmo de conseguir se conectar ao banco de dados.

---

## Erro 1 — UnicodeDecodeError no psycopg2

### Sintoma

```
File "psycopg2/__init__.py", line 135, in connect
    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe7 in position 78: invalid continuation byte
```

O comando `python manage.py makemigrations` falhava imediatamente, sem nenhuma mensagem útil sobre o banco de dados.

### Causa raiz

O driver `psycopg2-binary` (versão 2.9.10) possui um bug conhecido em sua extensão C que afeta sistemas Windows configurados com locale em Português.

O byte `0xe7` corresponde ao caractere `ç` na codificação Latin-1 (ISO 8859-1). Quando o PostgreSQL retorna uma mensagem de erro do sistema operacional (ex: "autenticação do tipo senha falhou"), o Windows entrega essa string na codificação do sistema (CP1252/Latin-1), mas o psycopg2 tenta decodificá-la como UTF-8, causando o crash.

O erro ocorre na camada C do driver, antes de qualquer código Python ter a chance de tratá-lo. Por isso, configurações como `PYTHONUTF8=1`, `PGCLIENTENCODING=UTF8` ou `chcp 65001` não resolvem o problema.

### Decisão

Substituir o `psycopg2-binary` pelo `psycopg` (versão 3), que:

- é o sucessor oficial do psycopg2;
- é mantido pelo mesmo autor;
- trata corretamente a codificação em todas as plataformas;
- é suportado nativamente pelo Django 5.x (detecção automática).

### Implementação

```bash
pip install "psycopg[binary]"
```

O Django utiliza o backend `django.db.backends.postgresql`, que a partir da versão 4.2+ detecta automaticamente qual driver está disponível (`psycopg` ou `psycopg2`), sem necessidade de alterar a configuração `ENGINE` no `settings.py`.

O `psycopg2-binary` não foi desinstalado, mas o Django prioriza o `psycopg` (v3) quando ambos estão presentes.

---

## Erro 2 — Falha de autenticação no PostgreSQL

### Sintoma

Após resolver o erro de codificação com o psycopg3, a mensagem real do banco de dados ficou visível:

```
psycopg.OperationalError: connection failed: FATAL: autenticação do tipo senha falhou para o usuário "pac_user"
```

O banco de dados estava rodando (confirmado via `docker exec pac_postgres pg_isready`), mas rejeitava a conexão com as credenciais corretas.

### Causa raiz

Havia um **PostgreSQL 18 instalado localmente** no Windows, escutando na porta 5432, **ao mesmo tempo** que o container Docker também expunha a porta 5432.

Verificação que confirmou o conflito:

```
netstat -ano | Select-String ":5432"

TCP  0.0.0.0:5432  LISTENING  14260  (com.docker.backend)
TCP  0.0.0.0:5432  LISTENING  7196   (postgres local)
```

Quando o Django tentava conectar em `localhost:5432`, o sistema operacional roteava a conexão para o PostgreSQL local (que tinha credenciais diferentes), não para o container Docker.

### Decisão

Alterar a porta exposta pelo container Docker de `5432` para `5433`, evitando o conflito com a instalação local.

Alternativas consideradas:

| Alternativa | Motivo da rejeição |
|---|---|
| Parar o PostgreSQL local | Requer permissão de administrador e pode afetar outros projetos do desenvolvedor |
| Desinstalar o PostgreSQL local | Intrusivo demais; o desenvolvedor pode precisar dele |
| **Remapear a porta do Docker** | **Escolhida.** Não intrusiva, isolada ao projeto, fácil de reverter |

### Implementação

Três arquivos foram alterados:

**docker-compose.yml** — porta do container:

```diff
 ports:
-  - "5432:5432"
+  - "5433:5432"
```

**pac/config/settings.py** — default do `DB_PORT`:

```diff
- 'PORT': config('DB_PORT', default='5432'),
+ 'PORT': config('DB_PORT', default='5433'),
```

**.env** — variável de ambiente local:

```diff
- DB_PORT=5432
+ DB_PORT=5433
```

Após as alterações, o container foi recriado com volume limpo:

```bash
docker compose down -v
docker compose up -d
```

---

## Resultado

Após ambas as correções, a conexão funcionou e todas as migrations foram geradas e aplicadas com sucesso:

```
Operations to perform:
  Apply all migrations: admin, auditoria, auth, catalogo, contenttypes,
                        demandas, dfd, grupos_contratacao, sessions,
                        unidades, usuarios, validacoes
Running migrations:
  Applying unidades.0001_initial... OK
  Applying usuarios.0001_initial... OK
  Applying auditoria.0001_initial... OK
  Applying auditoria.0002_initial... OK
  Applying catalogo.0001_initial... OK
  Applying demandas.0001_initial... OK
  Applying demandas.0002_initial... OK
  Applying dfd.0001_initial... OK
  Applying dfd.0002_initial... OK
  Applying grupos_contratacao.0001_initial... OK
  Applying validacoes.0001_initial... OK
  ...
```

---

## Observações para a equipe

1. **Porta padrão do projeto é 5433**, não 5432. Qualquer desenvolvedor com PostgreSQL instalado localmente não terá conflito.

2. **O driver de conexão é o `psycopg` (v3)**, não o `psycopg2`. Ambos estão instalados, mas o Django prioriza o v3.

3. Se futuramente o `psycopg2-binary` for removido do projeto, atualizar o `requirements.txt` para refletir a mudança:

```diff
- psycopg2-binary
+ psycopg[binary]
```
