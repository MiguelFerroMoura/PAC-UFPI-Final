# Sistema de Gestão do Plano Anual de Contratações (PAC) - UFPI

Sistema web para gerenciamento do Plano Anual de Contratações (PAC) da Universidade Federal do Piauí (UFPI).

---

# Sobre o projeto

O sistema PAC UFPI tem como objetivo centralizar o processo de cadastro, validação, consolidação e acompanhamento das demandas institucionais do Plano Anual de Contratações.

A proposta é desenvolver uma aplicação web simples, organizada e de fácil manutenção para a equipe, utilizando Django com renderização server-side e Bootstrap no frontend.

---

# Objetivo

O sistema permitirá:

- Cadastro de demandas por unidades;
- Gerenciamento de itens do catálogo;
- Validação e devolução de itens por administradores;
- Consolidação de demandas em DFD;
- Controle de status e fluxo das solicitações;
- Rastreabilidade e auditoria;
- Acompanhamento gerencial do PAC.

---

# Stack

## Backend

- Django
- Django ORM
- Django Admin

## Frontend

- Templates Django
- Bootstrap 5
- JavaScript puro

## Banco de dados

- PostgreSQL
- Supabase (deploy/MVP)

## Infraestrutura

- Docker Compose
- Render

---

# Arquitetura

A aplicação seguirá uma arquitetura:

- Monolítica;
- Modular por apps Django;
- Baseada no padrão MVC/MTV;
- Com comunicação REST pontual para ações assíncronas e futuras integrações.

## Organização arquitetural

- **Models** → persistência e estrutura dos dados;
- **Views** → fluxo e controle das requisições;
- **Templates** → renderização das páginas HTML;
- **Apps Django** → separação modular das responsabilidades do sistema.

---

# Estrutura do projeto

```txt
pac/
├── config/
│
├── apps/
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
├── templates/
│
├── static/
│
└── manage.py
```

---

# Módulos principais

| App Django | Responsabilidade |
|---|---|
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

- Docker
- Docker Compose
- Python 3.12+
- Git

---

## Clonar o projeto

```bash
git clone <url-do-repositorio>
cd pac
```

---

## Subir o PostgreSQL

```bash
docker compose up -d
```

---

## Criar ambiente virtual

```bash
python -m venv venv
```

### Linux/macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Executar migrations

```bash
python manage.py migrate
```

---

## Criar superusuário

```bash
python manage.py createsuperuser
```

---

## Rodar servidor local

```bash
python manage.py runserver
```

---

# Deploy

## Aplicação

- Render

## Banco de dados

- PostgreSQL no Supabase

---

# Observação institucional

Render e Supabase serão utilizados inicialmente para desenvolvimento, testes e MVP. A infraestrutura definitiva deverá ser validada com a STI/UFPI conforme políticas institucionais de segurança, disponibilidade e gestão de dados.

---

# Equipe

Projeto desenvolvido para apoio ao gerenciamento do Plano Anual de Contratações da UFPI.