# Arquitetura da Aplicação — PAC UFPI

Documento que descreve a arquitetura do Sistema de Gestão do Plano Anual de
Contratações (PAC) da Universidade Federal do Piauí (UFPI).

> Base: código-fonte em `pac/` e o planejamento em
> [`Planejamento sistema PAC UFPI.pdf`](Planejamento%20sistema%20PAC%20UFPI.pdf).

---

## 1. Visão geral

O PAC UFPI é uma **aplicação web monolítica** construída em **Django** com
renderização *server-side* (HTML via templates + Bootstrap 5). O objetivo é
centralizar o cadastro, a validação, a consolidação e o acompanhamento das
demandas do Plano Anual de Contratações.

Características arquiteturais principais:

- **Monolítica** — um único projeto/deploy Django.
- **Modular por apps** — cada domínio de negócio é um app Django isolado.
- **Padrão MTV (Model–Template–View)** — a variação do MVC adotada pelo Django.
- **Server-side rendering** — as páginas são montadas no servidor; JavaScript é
  usado de forma pontual (`static/js/main.js`).
- **Autenticação baseada em sessão** com um modelo de usuário customizado
  (`AUTH_USER_MODEL = 'usuarios.Usuario'`).

---

## 2. Camadas

```
┌──────────────────────────────────────────────────────────────┐
│  Navegador (Bootstrap 5 + JS puro)                           │
└──────────────────────────────────────────────────────────────┘
                     │  HTTP (sessão + CSRF)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  Middleware Django (Security, WhiteNoise, Session, CSRF,     │
│  Authentication, Messages, Clickjacking)                     │
└──────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  URLConf (config/urls.py → apps/<app>/urls.py)               │
└──────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  Views (function-based) — controle de fluxo e permissões     │
└──────────────────────────────────────────────────────────────┘
        │                         │                    │
        ▼                         ▼                    ▼
┌──────────────┐        ┌──────────────────┐   ┌──────────────┐
│ Forms        │        │ Models (ORM)     │   │ Templates    │
│ (validação)  │        │ persistência     │   │ (HTML)       │
└──────────────┘        └──────────────────┘   └──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Banco de dados   │
                    │ (SQLite / Postgres) │
                    └──────────────────┘
```

| Camada | Responsabilidade | Onde vive |
|---|---|---|
| **Model** | Estrutura e persistência dos dados; regras de domínio a nível de modelo | `apps/<app>/models.py` |
| **View** | Controle das requisições, permissões e orquestração | `apps/<app>/views.py` |
| **Form** | Validação e limpeza de entrada de dados | `apps/<app>/forms.py` |
| **Template** | Renderização HTML | `pac/templates/` |
| **URLConf** | Roteamento | `config/urls.py` + `apps/<app>/urls.py` |
| **Admin** | Backoffice administrativo | `apps/<app>/admin.py` |

---

## 3. Organização modular (apps Django)

O projeto é dividido em nove apps de domínio, todos sob `pac/apps/`, mais o
pacote de configuração `config/`.

| App | Responsabilidade | Estado atual |
|---|---|---|
| `usuarios` | Modelo de usuário customizado, perfis e autenticação | Modelo + admin + views JSON (stubs) |
| `unidades` | Cadastro das unidades organizacionais | Somente modelo/migração |
| `grupos_contratacao` | Governança por grupo de contratação | Somente modelo/migração |
| `catalogo` | Itens/serviços padronizados | Somente modelo/migração |
| `demandas` | Fluxo principal das demandas e itens | **Implementado** (CRUD + envio) |
| `validacoes` | Validação/devolução de itens | Implementado (com defeito conhecido) |
| `dfd` | Consolidação e vínculo de DFD | Implementado (parcial) |
| `dashboard` | Página inicial e indicadores gerenciais | Apenas `home` estático |
| `auditoria` | Histórico e rastreabilidade | Somente modelo/migração |

> O estado detalhado e as lacunas de cada app estão em
> [`05-pendencias.md`](05-pendencias.md).

### Estrutura de diretórios

```txt
pac/
├── config/                 # Projeto Django (settings, urls, wsgi, asgi)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                   # Apps de domínio
│   ├── usuarios/
│   ├── unidades/
│   ├── grupos_contratacao/
│   ├── catalogo/
│   ├── demandas/
│   ├── validacoes/
│   ├── dfd/
│   ├── dashboard/
│   └── auditoria/
│
├── templates/              # Templates HTML globais
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── crud/
│   ├── demandas/
│   ├── dfd/
│   └── validacoes/
│
├── static/                 # CSS, JS e imagens
│   ├── css/style.css
│   └── js/main.js
│
└── manage.py
```

Cada app segue a estrutura padrão Django: `models.py`, `views.py`, `urls.py`,
`forms.py`, `admin.py`, `apps.py`, `tests.py` e `migrations/`.

---

## 4. Modelo de dados (relacionamentos principais)

```
Unidade ──1:N── Usuario
   │                 │
   │ unidade_admin   │ usuario (responsável)
   ▼                 ▼
GrupoContratacao   Demanda ──1:N── ItemDemanda
   │                                    │
   │ grupo                              │ item_catalogo (opcional)
   ▼                                    ▼
ItemCatalogo ◄──────────────────── (referência)
                                        │
ItemDemanda ──1:N── Validacao           │
ItemDemanda ──N:M── DFD ── grupo ──► GrupoContratacao
LogAuditoria ── (modelo + objeto_id) ── referência genérica explícita
```

Pontos de modelagem relevantes:

- **`Demanda` não tem vínculo direto com `GrupoContratacao`.** O grupo é
  definido no nível do `ItemCatalogo`; itens de uma mesma demanda podem
  pertencer a grupos diferentes (ver docstring em
  [`demandas/models.py`](../pac/apps/demandas/models.py)).
- **Status independente por item** (`ItemDemanda.status`), atendendo à regra de
  negócio RN19 — itens da mesma demanda podem estar em estágios diferentes.
- **DFD ↔ Itens** é modelado como **ManyToMany** direto, sem tabela
  intermediária de consolidação; a lógica de agrupamento/soma fica na camada de
  views/queries.
- **`LogAuditoria`** usa referência genérica explícita (`modelo` + `objeto_id` +
  JSON de dados anteriores/novos) em vez de `ContentType`/`GenericForeignKey`,
  para manter o código simples.

---

## 5. Autenticação e perfis

- Modelo de usuário customizado `usuarios.Usuario` estende `AbstractUser`,
  acrescentando `siape`, `perfil` e `unidade`.
- Três perfis (`usuarios.Perfil`): **USUÁRIO**, **ADMIN** e **ADMIN MASTER**.
- Autenticação por sessão usando as views nativas do Django
  (`django.contrib.auth.views.LoginView`/`LogoutView`).
- Rotas de autenticação definidas em `config/urls.py`:
  `LOGIN_URL=/login/`, `LOGIN_REDIRECT_URL=/dashboard/`,
  `LOGOUT_REDIRECT_URL=/login/`.

> Observação: as views de negócio hoje usam `request.user.is_staff` como proxy
> de "administrador", e não o campo `perfil`. Ver
> [`05-pendencias.md`](05-pendencias.md).

---

## 6. Roteamento

O roteamento raiz está em [`config/urls.py`](../pac/config/urls.py) e delega
para os `urls.py` de cada app via `include()`:

| Prefixo | App | Observação |
|---|---|---|
| `/admin/` | Django Admin | Backoffice |
| `/` | `dashboard.views.home` | Página inicial |
| `/login/`, `/logout/` | auth do Django | Sessão |
| `/dashboard/` | `apps.dashboard` | **urls vazio** |
| `/demandas/` | `apps.demandas` | Fluxo principal |
| `/validacoes/` | `apps.validacoes` | Validação |
| `/catalogo/` | `apps.catalogo` | **urls vazio** |
| `/dfds/` | `apps.dfd` | DFD |
| `/unidades/` | `apps.unidades` | **urls vazio** |
| `/grupos/` | `apps.grupos_contratacao` | **urls vazio** |
| `/usuarios/` | `apps.usuarios` | Endpoints JSON |
| `/auditoria/` | `apps.auditoria` | **urls vazio** |

---

## 7. Frontend

- **Templates Django** com herança a partir de `templates/base.html`.
- **Bootstrap 5** e **Bootstrap Icons** carregados via CDN.
- **JavaScript puro** em `static/js/main.js` (sem framework SPA).
- **Django Messages Framework** para feedback ao usuário (sucesso/erro/aviso).
- Servir de estáticos via **WhiteNoise** (`CompressedManifestStaticFilesStorage`).

---

## 8. Infraestrutura e deploy

| Item | Tecnologia | Observação |
|---|---|---|
| Banco (dev) | **SQLite** | Configuração atual em `settings.py` |
| Banco (planejado) | **PostgreSQL** | `docker-compose.yml`, `.env.example`, README |
| Banco (MVP) | **Supabase** | Deploy inicial |
| Aplicação | **Render** | Deploy inicial |
| WSGI | **Gunicorn** | Produção |
| Estáticos | **WhiteNoise** | Sem CDN externo |
| Containerização | **Docker Compose** | Sobe apenas o Postgres em dev |

> Atenção: há uma **divergência** entre a configuração de banco em
> `settings.py` (SQLite) e o restante do planejamento (PostgreSQL). Registrado
> em [`05-pendencias.md`](05-pendencias.md).

A infraestrutura definitiva deverá ser validada com a **STI/UFPI** conforme
políticas institucionais de segurança, disponibilidade e gestão de dados.

---

## 9. Decisões arquiteturais (resumo)

1. **Monolito modular Django** — simplicidade de manutenção para a equipe, em
   vez de microsserviços.
2. **MTV server-side** — reduz complexidade de frontend; sem SPA.
3. **Usuário customizado desde o início** — evita migração dolorosa de
   `AUTH_USER_MODEL` posteriormente.
4. **Status por item** — flexibilidade no fluxo de validação (RN19).
5. **Auditoria por referência explícita** — previsibilidade e simplicidade em
   vez de `GenericForeignKey`.
6. **REST pontual/futuro** — comunicação REST prevista apenas para ações
   assíncronas e integrações futuras (ex.: SIPAC).
