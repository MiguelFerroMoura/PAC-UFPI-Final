# Stack Tecnológica — PAC UFPI

Tecnologias, bibliotecas e ferramentas utilizadas no projeto, conforme
`requirements.txt`, `settings.py`, `docker-compose.yml` e o README.

---

## 1. Visão geral

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12+ |
| Framework web | Django 5.1.8 |
| Persistência | Django ORM |
| Banco (dev, atual) | SQLite |
| Banco (planejado/produção) | PostgreSQL 16 / Supabase |
| Frontend | Templates Django + Bootstrap 5 + JS puro |
| Servidor de aplicação | Gunicorn |
| Estáticos | WhiteNoise |
| Configuração | python-decouple (`.env`) |
| Containerização | Docker Compose |
| Deploy (MVP) | Render (app) + Supabase (banco) |

---

## 2. Backend

### 2.1 Linguagem e framework

- **Python 3.12+** (pré-requisito no README).
- **Django 5.1.8** — framework web full-stack, base de todo o sistema.
- **Django ORM** — mapeamento objeto-relacional para acesso ao banco.
- **Django Admin** — backoffice administrativo pronto.
- **Django Auth** — autenticação por sessão e modelo de usuário customizado.

### 2.2 Dependências (`requirements.txt`)

| Pacote | Versão | Finalidade |
|---|---|---|
| `Django` | 5.1.8 | Framework web principal |
| `psycopg2-binary` | 2.9.10 | Driver PostgreSQL |
| `python-decouple` | 3.8 | Leitura de configuração via `.env` |
| `whitenoise` | 6.9.0 | Servir arquivos estáticos em produção |
| `gunicorn` | 23.0.0 | Servidor WSGI para produção |

> Nota: `psycopg2-binary` está presente, mas o `settings.py` atual aponta para
> **SQLite**. A troca para PostgreSQL ainda precisa ser efetivada (ver
> [`05-pendencias.md`](05-pendencias.md)).

---

## 3. Frontend

- **Templates Django** — renderização *server-side*.
- **Bootstrap 5.3.3** — framework CSS (via CDN em `base.html`).
- **Bootstrap Icons 1.11.3** — ícones (via CDN).
- **JavaScript puro** — sem framework SPA (`static/js/main.js`).
- **CSS próprio** — `static/css/style.css`.

---

## 4. Banco de dados

| Ambiente | Motor | Origem da configuração |
|---|---|---|
| Desenvolvimento (efetivo) | **SQLite** (`db.sqlite3`) | `config/settings.py` |
| Desenvolvimento (planejado) | **PostgreSQL 16** | `docker-compose.yml`, `.env.example` |
| MVP / produção inicial | **Supabase** (PostgreSQL) | README |

Configuração do container Postgres (`docker-compose.yml`):

- Imagem `postgres:16`
- Banco `pac_db`, usuário `pac_user`
- Porta host **5433** → container 5432
- Volume nomeado `pgdata` para persistência

---

## 5. Infraestrutura e deploy

| Componente | Tecnologia | Observação |
|---|---|---|
| Servidor WSGI | **Gunicorn** | Produção |
| Estáticos | **WhiteNoise** | `CompressedManifestStaticFilesStorage` |
| Container de banco | **Docker Compose** | Sobe apenas o Postgres em dev |
| Hospedagem da app | **Render** | Deploy MVP |
| Banco gerenciado | **Supabase** | Deploy MVP |

> Render e Supabase são usados inicialmente para desenvolvimento, testes e MVP.
> A infraestrutura definitiva deverá ser validada com a **STI/UFPI**.

---

## 6. Configuração e ambiente

- **`python-decouple`** lê variáveis de `.env` (`SECRET_KEY`, `DEBUG`,
  `ALLOWED_HOSTS`, credenciais de banco).
- `.env.example` versionado como modelo.
- **Internacionalização**: `LANGUAGE_CODE = 'pt-br'`,
  `TIME_ZONE = 'America/Fortaleza'`, `USE_TZ = True`.

---

## 7. Segurança (mecanismos do framework)

- Middlewares de segurança padrão (CSRF, Clickjacking/X-Frame-Options,
  SecurityMiddleware).
- Validadores de senha do Django (`AUTH_PASSWORD_VALIDATORS`).
- Autenticação por sessão.
- Segredos externalizados via `.env`.

> Requisitos de segurança do planejamento ainda pendentes (login institucional,
> auditoria/logs completos) estão detalhados em
> [`05-pendencias.md`](05-pendencias.md).

---

## 8. Ferramentas de desenvolvimento

- **Git** — controle de versão.
- **Docker / Docker Compose** — banco local.
- **`manage.py`** — CLI do Django (migrate, runserver, createsuperuser, etc.).
- **venv** — ambiente virtual Python.

---

## 9. O que NÃO está no stack (ainda)

Itens mencionados no planejamento mas sem dependência/implementação atual:

- Biblioteca de **exportação** para PDF/XLS/Excel (RF16/RF23).
- Backend/serviço de **e-mail** para notificações (RF11).
- Camada de **API REST** (prevista apenas para uso futuro/pontual).
- Integração com **SIPAC/PGC** (futuro).
- Ferramentas de **teste** configuradas além do `tests.py` padrão (arquivos de
  teste estão vazios).
