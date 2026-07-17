# Stack Tecnológica — PAC UFPI

Tecnologias, bibliotecas e ferramentas utilizadas no projeto, conforme
`requirements.txt`, `settings.py`, `frontend/package.json`, `Dockerfile` e o
README.

---

## 1. Visão geral

| Camada | Tecnologia |
|---|---|
| Linguagem (back-end) | Python 3.11+ |
| Framework web | Django 5.1.8 |
| API REST | Django REST Framework 3.15 |
| CORS | django-cors-headers 4.4 |
| Persistência | Django ORM |
| Banco (local e produção) | SQLite |
| Linguagem (front-end) | JavaScript (ES2021+) |
| Front-end | React 18 (SPA) |
| Build/dev do front | Vite 5 |
| Roteamento (front) | React Router 6 |
| Estilos (front) | Bootstrap 5 + Bootstrap Icons |
| Testes (front) | Vitest + React Testing Library |
| Servidor de aplicação | Gunicorn |
| Estáticos | WhiteNoise |
| Configuração | python-decouple (`.env`) |
| Containerização | Docker (imagem de produção multi-stage) |

---

## 2. Back-end

### 2.1 Linguagem e framework

- **Python 3.11+**.
- **Django 5.1.8** — framework web, base do back-end.
- **Django REST Framework** — camada de API REST consumida pelo front-end React.
- **Django ORM** — mapeamento objeto-relacional para acesso ao banco.
- **Django Admin** — backoffice administrativo pronto.
- **Django Auth** — autenticação por sessão e modelo de usuário customizado.

### 2.2 Dependências (`requirements.txt`)

| Pacote | Versão | Finalidade |
|---|---|---|
| `Django` | 5.1.8 | Framework web principal |
| `djangorestframework` | 3.15.2 | API REST |
| `django-cors-headers` | 4.4.0 | Liberação de CORS para o front-end |
| `python-decouple` | 3.8 | Leitura de configuração via `.env` |
| `whitenoise` | 6.9.0 | Servir arquivos estáticos em produção |
| `gunicorn` | 23.0.0 | Servidor WSGI para produção |

> O banco é **SQLite** — embutido no Python, sem driver externo.

### 2.3 A API REST (`apps/api`)

- **Serializers** (`apps/api/serializers.py`) convertem os modelos em JSON.
- **ViewSets/Views** (`apps/api/views.py`) implementam as regras de negócio.
- **Rotas** (`apps/api/urls.py`) sob o prefixo `/api/`, com um `DefaultRouter`.
- **Autenticação por sessão** (`SessionAuthentication`) + permissão padrão
  `IsAuthenticated`, com paginação de 20 itens por página.

Endpoints principais:

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login/` | Autentica e abre sessão |
| POST | `/api/auth/logout/` | Encerra a sessão |
| GET | `/api/auth/me/` | Usuário autenticado |
| GET/POST | `/api/demandas/` | Lista/cria demandas |
| POST | `/api/demandas/{id}/itens/` | Adiciona item |
| POST | `/api/demandas/{id}/enviar/` | Envia para validação |
| GET | `/api/validacoes/pendentes/` | Itens aguardando validação |
| POST | `/api/validacoes/decidir/` | Valida ou devolve item |
| GET | `/api/dfds/disponiveis/` | Itens validados sem DFD |
| POST | `/api/dfds/consolidar/` | Cria DFD a partir de itens |
| GET | `/api/dashboard/stats/` | Indicadores gerenciais |
| GET | `/api/catalogo/`, `/api/grupos/`, `/api/unidades/` | Recursos de referência |

---

## 3. Front-end (React SPA)

Aplicação **Single Page Application** independente, em `frontend/`, que consome
a API REST.

| Item | Tecnologia |
|---|---|
| Biblioteca de UI | **React 18** |
| Build/dev server | **Vite 5** (porta 5173 em dev) |
| Roteamento | **React Router 6** |
| Estilos | **Bootstrap 5** + **Bootstrap Icons** |
| Testes | **Vitest** + **React Testing Library** + jsdom |
| Lint | **ESLint** |

Organização (`frontend/src/`):

- `api/client.js` — cliente HTTP (fetch com cookies de sessão + CSRF).
- `auth/AuthContext.jsx` — contexto de autenticação.
- `components/` — `Layout`, `ProtectedRoute`, `Spinner`.
- `pages/` — uma tela por recurso (Login, Home, Dashboard, Demandas, Itens,
  Catálogo, Validações, DFDs).
- `routes.jsx` — mapa central de rotas.

O desenvolvimento seguiu **TDD**: cada tela/módulo tem testes escritos antes da
implementação (arquivos `*.test.jsx`).

---

## 4. Banco de dados

| Ambiente | Motor | Origem da configuração |
|---|---|---|
| Desenvolvimento | **SQLite** (`db.sqlite3`) | `config/settings.py` |
| Produção | **SQLite** (`db.sqlite3`) | `config/settings.py` |

> O PostgreSQL/Docker Compose foi removido do projeto. O banco é SQLite tanto
> localmente quanto em produção.

---

## 5. Infraestrutura e deploy

| Componente | Tecnologia | Observação |
|---|---|---|
| Servidor WSGI | **Gunicorn** | Produção |
| Estáticos | **WhiteNoise** | `CompressedManifestStaticFilesStorage` |
| Imagem de produção | **Docker** | Multi-stage: build React + app Django |
| Banco | **SQLite** | Arquivo `db.sqlite3` |

O `Dockerfile` tem dois estágios: o primeiro (Node) gera o build do React; o
segundo (Python) instala o Django, copia o build para `frontend_build/` e serve
tudo com Gunicorn + WhiteNoise.

> A infraestrutura definitiva deverá ser validada com a **STI/UFPI**.

---

## 6. Configuração e ambiente

- **`python-decouple`** lê variáveis de `.env` (`SECRET_KEY`, `DEBUG`,
  `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`).
- `.env.example` versionado como modelo.
- **Internacionalização**: `LANGUAGE_CODE = 'pt-br'`,
  `TIME_ZONE = 'America/Fortaleza'`, `USE_TZ = True`.
- **CORS**: `CORS_ALLOWED_ORIGINS` libera o front-end (Vite, porta 5173) a
  consumir a API com credenciais (cookies de sessão).

---

## 7. Segurança (mecanismos do framework)

- Middlewares de segurança padrão (CSRF, Clickjacking/X-Frame-Options,
  SecurityMiddleware) + CORS controlado por origem.
- Autenticação por sessão do DRF; endpoints exigem usuário autenticado.
- Validadores de senha do Django (`AUTH_PASSWORD_VALIDATORS`).
- Segredos externalizados via `.env`.

---

## 8. Ferramentas de desenvolvimento

- **Git** — controle de versão.
- **Node.js/npm** — build e testes do front-end.
- **`manage.py`** — CLI do Django (migrate, runserver, test, etc.).
- **venv** — ambiente virtual Python.
- **Docker** — empacotamento da imagem de produção.

---

## 9. O que NÃO está no stack (ainda)

Itens mencionados no planejamento mas sem dependência/implementação atual:

- Biblioteca de **exportação** para PDF/XLS/Excel (RF16/RF23).
- Backend/serviço de **e-mail** para notificações (RF11).
- Integração com **SIPAC/PGC** (futuro).
