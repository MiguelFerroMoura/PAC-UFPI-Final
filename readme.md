# Sistema de Gestão do Plano Anual de Contratações (PAC) - UFPI

Sistema web para gerenciamento do Plano Anual de Contratações (PAC) da Universidade Federal do Piauí (UFPI).

---

# Sobre o projeto

O sistema PAC UFPI tem como objetivo centralizar o processo de cadastro, validação, consolidação e acompanhamento das demandas institucionais do Plano Anual de Contratações.

A aplicação é composta por duas partes desacopladas:

- **Back-end** — API REST em **Django + Django REST Framework**, responsável pelas regras de negócio, persistência e autenticação.
- **Front-end** — **SPA (Single Page Application) em React**, que consome a API REST.

---

# Objetivo

O sistema permite:

- Cadastro de demandas por unidades;
- Gerenciamento de itens do catálogo;
- Validação e devolução de itens por administradores;
- Consolidação de demandas em DFD;
- Controle de status e fluxo das solicitações;
- Rastreabilidade e auditoria;
- Acompanhamento gerencial do PAC.

---

# Stack

## Back-end

- Django 5.1
- Django REST Framework (API REST)
- Django ORM
- Django Admin
- django-cors-headers (CORS para o front-end)

## Front-end

- React 18 (SPA)
- Vite (build e servidor de desenvolvimento)
- React Router (roteamento)
- Bootstrap 5 (estilos)
- Vitest + React Testing Library (testes)

## Banco de dados

- SQLite (local e produção)

## Infraestrutura

- Gunicorn (servidor WSGI)
- WhiteNoise (arquivos estáticos)
- Docker (imagem de produção multi-stage: build do React + app Django)

---

# Arquitetura

- **Back-end desacoplado** expondo uma **API REST** sob o prefixo `/api/`.
- **Front-end SPA** independente, consumindo a API via `fetch` com autenticação por sessão (cookies) + CSRF.
- **Monolito modular** no back-end: cada domínio é um app Django isolado.
- **Autenticação por sessão** com modelo de usuário customizado.

```txt
┌─────────────────────────┐        HTTP/JSON        ┌──────────────────────────┐
│  React SPA (Vite)       │  ───────────────────▶   │  Django REST Framework   │
│  Bootstrap 5            │  ◀───────────────────   │  /api/ (sessão + CSRF)    │
│  porta 5173 (dev)       │                         │  porta 8000               │
└─────────────────────────┘                         └──────────────────────────┘
                                                                 │
                                                                 ▼
                                                          ┌──────────────┐
                                                          │  SQLite      │
                                                          └──────────────┘
```

## Módulos principais (apps Django)

| App Django | Responsabilidade |
|---|---|
| api | Camada de API REST (serializers, viewsets, rotas) |
| usuarios | Usuários, autenticação e permissões |
| unidades | Cadastro das unidades |
| grupos_contratacao | Governança por grupos de contratação |
| catalogo | Itens e serviços disponíveis |
| demandas | Fluxo principal das demandas |
| validacoes | Validação e devolução de itens |
| dfd | Consolidação e vínculo de DFD |
| dashboard | Indicadores gerenciais |
| auditoria | Histórico e rastreabilidade |

---

# Fluxo básico do sistema

```txt
Usuário cria demanda
        ↓
Usuário adiciona itens
        ↓
Usuário envia demanda
        ↓
ADMIN valida ou devolve
        ↓
Itens validados são consolidados
        ↓
DFD é vinculado
        ↓
Dashboard acompanha execução
```

---

# Perfis do sistema

| Perfil | Responsabilidade |
|---|---|
| USUÁRIO | Cadastro e acompanhamento das demandas |
| ADMIN | Validação, devolução e consolidação |
| ADMIN MASTER | Governança geral do sistema e do PAC |

---

# Como rodar localmente

## Pré-requisitos

- Python 3.11+
- Node.js 20+ e npm
- Git

---

## Clonar o projeto

```bash
git clone <url-do-repositorio>
cd PAC-UFPI-Final
```

---

## Back-end (Django + API REST)

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Copiar variáveis de ambiente
cp .env.example .env      # (no Windows: copy .env.example .env)

# 4. Aplicar migrações (SQLite — sem configuração extra)
cd pac
python manage.py migrate

# 5. Criar superusuário
python manage.py createsuperuser

# 6. Rodar o servidor da API
python manage.py runserver   # API em http://localhost:8000/api/
```

---

## Front-end (React + Vite)

Em outro terminal:

```bash
cd frontend
npm install
npm run dev        # SPA em http://localhost:5173
```

Por padrão, o front-end consome a API em `http://localhost:8000/api`. Para
apontar para outra URL, defina `VITE_API_URL` (ex.: em `frontend/.env`).

---

## Testes

```bash
# Back-end (API REST)
cd pac
python manage.py test

# Front-end (React)
cd frontend
npm test
```

---

# Deploy

A imagem Docker de produção (`Dockerfile`) é multi-stage:

1. **Estágio Node** — instala dependências e gera o build do React (`frontend/dist`).
2. **Estágio Python** — instala o Django, copia o build do React e serve tudo
   com **Gunicorn + WhiteNoise**, usando **SQLite** como banco.

```bash
docker build -t pac-ufpi .
docker run -p 8000:8000 -e SECRET_KEY=troque-isto pac-ufpi
```

---

# Observação institucional

A infraestrutura definitiva deverá ser validada com a STI/UFPI conforme políticas institucionais de segurança, disponibilidade e gestão de dados.

---

# Equipe

Projeto desenvolvido para apoio ao gerenciamento do Plano Anual de Contratações da UFPI.
