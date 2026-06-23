# Sistema de Gestão do Plano Anual de Contratações (PAC) - UFPI

## Visão Geral

O Sistema de Gestão do Plano Anual de Contratações (PAC) da UFPI tem como objetivo centralizar o cadastro, validação, consolidação e acompanhamento das demandas institucionais relacionadas ao Plano Anual de Contratações da Universidade Federal do Piauí.

O projeto foi concebido para substituir fluxos manuais e formulários descentralizados utilizados atualmente no processo de planejamento das contratações, especialmente no contexto do PAC e das demandas de TIC.

O sistema segue os princípios estabelecidos pela:

- Lei nº 14.133/2021;
- Decreto nº 10.947/2022;
- IN nº 94/2022.

---

# Contexto do PAC, PGC e DFD

O PAC (Plano Anual de Contratações) organiza, de forma antecipada, as compras e contratações previstas pela instituição.

O PGC (Plano de Gerenciamento de Contratações) é o sistema do Governo Federal onde essas informações são registradas oficialmente.

O DFD (Documento de Formalização da Demanda) é o documento que formaliza e justifica cada necessidade de contratação.

Fluxo conceitual:

```txt
PAC → planejamento institucional

PGC → sistema governamental de registro

DFD → documento que formaliza a demanda
```

O sistema PAC UFPI atuará como camada institucional de gestão e consolidação das demandas antes do envio oficial ao PGC.

---

# Objetivos do Sistema

O sistema deverá permitir:

- Levantamento estruturado de demandas;
- Consolidação por unidades requisitantes;
- Controle de prazos legais;
- Padronização das solicitações;
- Governança por grupo de contratação;
- Gestão de catálogo institucional;
- Geração e vinculação de DFD;
- Auditoria e rastreabilidade;
- Dashboards gerenciais;
- Integração futura com SIPAC.

---

# Escopo

O sistema abrangerá:

- Cadastro e gestão de demandas pelas unidades;
- Administração de catálogo por grupo de contratação;
- Controle de acesso por perfil;
- Fluxo de validação e consolidação;
- Vinculação de DFD;
- Monitoramento gerencial;
- Exportação de dados;
- Rastreabilidade completa.

---

# Arquitetura Técnica

A solução seguirá uma arquitetura:

- Monolítica;
- Modular por apps Django;
- Baseada no padrão MVC/MTV;
- Com renderização server-side;
- Utilizando comunicação REST pontual.

---

# Stack Tecnológica

## Backend

- Django
- Django ORM
- Django Admin

## Frontend

- Templates Django
- Bootstrap 5
- JavaScript puro

## Banco de Dados

- PostgreSQL
- Supabase (deploy/MVP)

## Infraestrutura

- Docker Compose
- Render

---

# Arquitetura da Solução

## Monólito Modular

Todos os módulos ficam na mesma aplicação Django e compartilham o mesmo banco de dados.

Vantagens:

- Menor complexidade;
- Deploy simplificado;
- Autenticação centralizada;
- Facilidade de manutenção;
- Melhor onboarding da equipe.

---

## MVC / MTV

O Django seguirá o padrão MTV:

| Camada | Responsabilidade |
|---|---|
| Models | Persistência e estrutura dos dados |
| Views | Fluxo e controle das requisições |
| Templates | Renderização HTML |

---

## API REST

O sistema utilizará endpoints REST apenas quando necessário:

- validações assíncronas;
- chamadas fetch;
- integrações futuras;
- ações específicas.

O sistema NÃO será uma SPA.

---

# Arquitetura de Implantação

```txt
Navegador
    ↓ HTTP
Render Web Service
    ↓
Django + Templates
Views + Forms + Services + Models
    ↓ SQL
Supabase PostgreSQL
```

---

# Organização do Projeto Django

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

# Módulos do Sistema

| App Django | Responsabilidade |
|---|---|
| usuarios | Usuários, autenticação e permissões |
| unidades | Cadastro das unidades |
| grupos_contratacao | Governança por grupos |
| catalogo | Itens e serviços |
| demandas | Fluxo principal das demandas |
| validacoes | Validação e devolução |
| dfd | Consolidação e vínculo de DFD |
| dashboard | Indicadores gerenciais |
| auditoria | Histórico e rastreabilidade |

---

# Fluxo Interno no Django

```txt
urls.py
    ↓
views.py
    ↓
forms.py
    ↓
services.py
    ↓
models.py
```

---

# Usuários do Sistema

Perfis previstos:

- Reitoria;
- Pró-Reitorias;
- Superintendências;
- Diretores;
- Órgãos suplementares;
- Auditoria Interna;
- Procuradoria Federal.

---

# Modelo de Governança

Cada grupo de contratação possui uma unidade ADMIN responsável por:

- Consolidar demandas;
- Gerenciar catálogo;
- Validar solicitações;
- Inserir informações no PGC;
- Registrar DFD.

Exemplos:

| Grupo | Unidade ADMIN |
|---|---|
| TIC | STI |
| PREUNI | Prefeitura |
| Almoxarifado | Divisão de Almoxarifado |

---

# Perfis do Sistema

## USUÁRIO

Responsável por:

- cadastrar demandas;
- editar rascunhos;
- acompanhar solicitações;
- enviar demandas.

---

## ADMIN

Responsável por:

- validar itens;
- devolver solicitações;
- gerenciar catálogo;
- consolidar itens;
- vincular DFD;
- gerenciar unidades vinculadas.

---

## ADMIN MASTER

Responsável por:

- gerenciar ADMINs;
- configurar calendário do PAC;
- monitorar execução geral;
- controlar grupos de contratação.

---

# Fluxo Principal do Sistema

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

# Funcionalidades do Usuário

O sistema deverá permitir:

- inclusão de itens;
- seleção via catálogo;
- inclusão manual;
- edição de rascunhos;
- envio de solicitações;
- exportação PDF/XLS;
- acompanhamento de status.

---

# Campos Obrigatórios por Item

Cada item deverá possuir:

- quantidade;
- data prevista;
- prioridade;
- justificativa de prioridade;
- justificativa de necessidade;
- valor estimado;
- indicação orçamentária.

---

# Regras Funcionais

## Regras Gerais

- Não permitir duplicidade;
- Soma automática de quantidades;
- Tooltips configuráveis;
- Auto salvamento;
- Histórico de alterações;
- Justificativa obrigatória em devoluções.

---

# Status do Sistema

## Status possíveis

- Rascunho
- Aguardando Validação
- Devolvido
- Validado
- Consolidado no DFD
- Cancelado

---

# Consolidação

O sistema deverá permitir:

- agrupamento de itens;
- soma automática;
- consolidação por categoria;
- vínculo com DFD;
- propagação do DFD aos itens relacionados.

---

# Dashboard Gerencial

## Dashboard ADMIN

Indicadores:

- % de unidades que enviaram;
- valor total estimado;
- valor por unidade;
- total por tipo de item;
- quantitativo por status;
- controle de prazos;
- identificação de atrasos.

---

## Dashboard ADMIN MASTER

Indicadores:

- visão geral do PAC;
- percentual consolidado;
- percentual com DFD;
- ranking de demandas;
- acompanhamento institucional.

---

# Rastreabilidade

Cada item deverá possuir:

- identificador único;
- histórico completo;
- unidade solicitante;
- usuário responsável;
- número do DFD;
- número do processo;
- link público.

---

# Requisitos Funcionais

| Código | Descrição |
|---|---|
| RF01 | Autenticação integrada |
| RF02 | Controle de usuários |
| RF03 | Gestão de catálogo |
| RF04 | Cadastro de demandas |
| RF05 | Inclusão e alteração de itens |
| RF06 | Não duplicidade |
| RF08 | Tooltips |
| RF09 | Controle de prazos |
| RF10 | Dashboard |
| RF11 | Notificações |
| RF12 | Gestão de ADMINs |
| RF14 | Salvar rascunho |
| RF15 | Enviar solicitação |
| RF16 | Exportação PDF/XLS |
| RF17 | Validação por item |
| RF19 | Consolidação |
| RF20 | Vinculação de DFD |
| RF24 | Auditoria completa |

---

# Regras de Negócio

| Código | Regra |
|---|---|
| RN01 | Apenas gestores autorizados podem solicitar |
| RN03 | Prioridade para itens do catálogo |
| RN04 | Proibição de duplicidade |
| RN05 | Justificativa obrigatória |
| RN07 | Governança por grupo |
| RN08 | Respeito aos prazos |
| RN10 | Permissões por perfil |
| RN11 | ID único por item |
| RN12 | Vinculação ao DFD |
| RN15 | Atualização de status pelo ADMIN |
| RN16 | Consolidação apenas de itens validados |
| RN19 | Independência de status por item |

---

# Requisitos Não Funcionais

- Segurança;
- Login institucional;
- Auditoria;
- Usabilidade;
- Disponibilidade web;
- Performance;
- Escalabilidade.

---

# Rotas Principais

| Área | Rota |
|---|---|
| Login | `/login/` |
| Dashboard | `/dashboard/` |
| Demandas | `/demandas/` |
| Nova demanda | `/demandas/nova/` |
| Validações | `/validacoes/` |
| Catálogo | `/catalogo/` |
| DFD | `/dfds/` |
| Administração | `/admin/` |

---

# Deploy e Ambiente

| Componente | Tecnologia |
|---|---|
| Aplicação | Render |
| Banco PostgreSQL | Supabase |
| Ambiente local | PostgreSQL via Docker Compose |
| Arquivos estáticos | WhiteNoise |
| Servidor Django | Gunicorn |

---

# Ambiente Local

Fluxo recomendado:

```bash
docker compose up -d

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```

---

# Formulário Atual de TIC

O formulário atual utilizado pela STI contém campos como:

- setor/unidade;
- categoria;
- descrição;
- preço unitário;
- quantidade;
- justificativa;
- detalhamento técnico.

O sistema PAC deverá absorver e estruturar esse fluxo diretamente dentro da aplicação web.

---

# Próximos Passos

1. Configurar projeto Django;
2. Configurar PostgreSQL via Docker Compose;
3. Criar apps principais;
4. Implementar models iniciais;
5. Configurar Django Admin;
6. Implementar fluxo de demandas;
7. Implementar validações;
8. Configurar deploy inicial.

---

# Observação Institucional

Render e Supabase serão utilizados inicialmente para desenvolvimento, testes e MVP.

A infraestrutura definitiva deverá ser validada com a STI/UFPI conforme políticas institucionais de segurança, disponibilidade e gestão de dados.

---

# Fontes

- Arquitetura proposta do PAC UFPI :contentReference[oaicite:0]{index=0}
- Planejamento do sistema PAC UFPI :contentReference[oaicite:1]{index=1}
- Formulário TIC 2026 UFPI :contentReference[oaicite:2]{index=2}