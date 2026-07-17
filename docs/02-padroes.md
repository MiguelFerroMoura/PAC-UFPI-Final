# Padrões Utilizados — PAC UFPI

Este documento descreve os padrões adotados no projeto, separados em
**padrões do Django** (convenções do framework) e **padrões de projeto**
(*design patterns* clássicos e do ecossistema Django).

> **Nota de arquitetura:** o front-end passou a ser uma **SPA React** que consome
> a **API REST** (`apps/api`, Django REST Framework). Os padrões de *template*
> descritos abaixo (MTV, herança de `base.html`) referem-se à camada server-side
> **legada** — mantida como referência. No back-end atual, a camada de
> apresentação é substituída por **serializers + viewsets** do DRF, e a
> renderização das telas ocorre no React (`frontend/`).

---

## 1. Padrões do Django

### 1.1 MTV (Model–Template–View)

O Django implementa uma variação do MVC chamada **MTV**:

- **Model** → dados e persistência (`apps/<app>/models.py`).
- **Template** → apresentação HTML (`pac/templates/`).
- **View** → lógica de controle e orquestração (`apps/<app>/views.py`).

O "Controller" do MVC clássico corresponde ao próprio framework (roteamento +
view).

### 1.2 Projeto dividido em Apps

Cada domínio de negócio é um **app Django** independente e reutilizável, listado
em `INSTALLED_APPS` (`config/settings.py`). Os apps de domínio ficam agrupados
sob o pacote `apps/` (`apps.usuarios`, `apps.demandas`, etc.).

### 1.3 Custom User Model

Uso de `AbstractUser` para estender o usuário padrão, definido cedo no projeto
via `AUTH_USER_MODEL = 'usuarios.Usuario'`
([`usuarios/models.py`](../pac/apps/usuarios/models.py)). Boa prática recomendada
pela documentação oficial do Django.

### 1.4 Function-Based Views (FBV)

As views são funções decoradas com `@login_required`
(ex.: [`demandas/views.py`](../pac/apps/demandas/views.py)), em vez de
Class-Based Views. Padrão explícito e direto, adequado ao tamanho do projeto.

### 1.5 ModelForm

Formulários derivam de `forms.ModelForm`
([`demandas/forms.py`](../pac/apps/demandas/forms.py)), reaproveitando a
definição do modelo. Uso de:

- `Meta.fields` / `Meta.exclude` para selecionar campos;
- `Meta.widgets` para aplicar classes Bootstrap;
- `clean()` para validações compostas (ex.: quantidade e valor > 0).

### 1.6 TextChoices (enumerações)

Enumerações de domínio via `models.TextChoices`:

- `usuarios.Perfil`
- `demandas.StatusDemanda`, `demandas.Prioridade`, `demandas.TipoItem`
- `catalogo.TipoItem`
- `validacoes.TipoAcao`

Padroniza rótulos legíveis e valores persistidos.

### 1.7 URL namespacing

Cada app declara `app_name` no seu `urls.py` e é incluído com `include()` no
`config/urls.py`. As referências usam o namespace (`demandas:detalhe`,
`validacoes:lista_pendentes`, `dfds:lista`), inclusive nos templates via
`{% url %}`.

### 1.8 ORM, `related_name` e otimização de queries

- Relacionamentos com `ForeignKey`/`ManyToManyField` e `related_name` explícito
  (`demandas`, `itens`, `validacoes`, `dfds`, etc.).
- Otimização com `select_related()` (FK) e `prefetch_related()` (reverso/M2M)
  nas listagens e detalhes (ex.: `Demanda.objects.select_related("unidade",
  "usuario").prefetch_related("itens")`).
- `on_delete` semântico: `PROTECT` para dados de referência (unidade, usuário,
  item de catálogo), `CASCADE` para itens dependentes, `SET_NULL` para o autor
  do log de auditoria.

### 1.9 Migrations

Esquema versionado via migrações geradas pelo Django (`apps/<app>/migrations/`).

### 1.10 Messages Framework

Feedback ao usuário via `django.contrib.messages`
(`messages.success/error/warning`), renderizado no `base.html`.

### 1.11 Middleware pipeline

Pilha padrão de middlewares de segurança/sessão em `settings.py`
(Security, WhiteNoise, Session, Common, CSRF, Authentication, Messages,
Clickjacking).

### 1.12 Settings via variáveis de ambiente

Uso de **`python-decouple`** (`config(...)`) para externalizar `SECRET_KEY`,
`DEBUG`, `ALLOWED_HOSTS` e credenciais, com `.env.example` versionado.

### 1.13 Personalização do Django Admin

`ModelAdmin` customizados com `list_display`, `list_filter`, `search_fields`,
`fieldsets` e `filter_horizontal` (ex.:
[`usuarios/admin.py`](../pac/apps/usuarios/admin.py) estendendo `UserAdmin`, e
[`dfd/admin.py`](../pac/apps/dfd/admin.py)).

---

## 2. Padrões de Projeto (Design Patterns)

Padrões clássicos e do ecossistema Django presentes (ou previstos) no código.

### 2.1 Active Record (via Django ORM)

Cada classe de `models.py` encapsula dados **e** comportamento de persistência
(`save()`, `objects`), característico do padrão **Active Record**. Ex.: override
de `save()` em `ItemDemanda`/`Demanda` e cálculo de `valor_total`.

### 2.2 State / Máquina de Estados

O ciclo de vida da demanda e do item é uma **máquina de estados** explícita:

- Estados em `demandas.StatusDemanda`.
- Em [`demandas/constants.py`](../pac/apps/demandas/constants.py) há um mapa de
  transições permitidas (`TRANSICOES_STATUS_DEMANDA`) e a função-guarda
  `pode_transicionar_status(status_atual, novo_status)`.

> Ressalva: existem **duas** definições de `StatusDemanda` (uma em `models.py`,
> outra em `constants.py`) com valores divergentes, e a função de transição
> ainda **não é usada** pelas views. Ver [`05-pendencias.md`](05-pendencias.md).

### 2.3 Template Method (herança de templates)

A herança de templates (`base.html` com blocos sobrescritos pelos filhos) é uma
aplicação do padrão **Template Method** na camada de apresentação.

### 2.4 Form Object / Validação encapsulada

Os `ModelForm` atuam como **Form Objects**, encapsulando a validação de entrada
fora da view (método `clean()`).

### 2.5 Front Controller

O `URLConf` do Django atua como **Front Controller**: um ponto único de entrada
(`config/urls.py`) que despacha as requisições para as views apropriadas.

### 2.6 Decorator

Uso do padrão **Decorator** via `@login_required` para adicionar verificação de
autenticação de forma transversal às views.

### 2.7 Audit Log / Memento (parcial)

O modelo `LogAuditoria` guarda `dados_anteriores`/`dados_novos` (JSON),
aproximando-se de um **Audit Log** com snapshots no estilo **Memento**.

> Ressalva: o modelo existe, mas **nenhum código escreve logs** ainda (não há
> signals/serviço de auditoria). Ver [`05-pendencias.md`](05-pendencias.md).

### 2.8 Padrões previstos / recomendados (ainda não implementados)

- **Service Layer** — a docstring do DFD indica que "a lógica de agrupamento e
  soma será tratada na camada de serviços/queries"; hoje essa lógica está nas
  views. Recomenda-se extrair para `services.py` por app.
- **Observer (signals)** — natural para disparar auditoria e notificações por
  e-mail (RF11/RF24) de forma desacoplada.
- **Strategy** — para as diferentes exportações (PDF/XLS/Excel — RF16/RF23).

---

## 3. Convenções de código observadas

- **Idioma**: domínio e identificadores em **português** (`Demanda`,
  `unidade_admin`, `valor_total`); docstrings explicativas em cada modelo.
- **Campos de timestamp** padronizados: `criado_em` (`auto_now_add`) e
  `atualizado_em` (`auto_now`).
- **`verbose_name`/`verbose_name_plural`** e `Meta.ordering` em todos os modelos.
- **`__str__`** significativo em todos os modelos.
- **Rastreabilidade de regras**: comentários citam explicitamente os requisitos
  (ex.: `# Status independente por item (RN19).`, `RF17`, `RN05`).
