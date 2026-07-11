# Pendências da Aplicação — PAC UFPI

Levantamento **completo** das pendências do sistema, **validado** contra o
documento de requisitos
[`Planejamento sistema PAC UFPI.pdf`](Planejamento%20sistema%20PAC%20UFPI.pdf)
e contra o código-fonte em `pac/`.

Legenda de estado:

- ✅ **Implementado**
- ⚠️ **Parcial** (existe, mas incompleto ou com defeito)
- ❌ **Pendente** (não implementado)

---

## 1. Defeitos / bugs conhecidos (prioridade alta)

Estes itens quebram funcionalidades já escritas.

| # | Defeito | Local | Impacto |
|---|---|---|---|
| B1 | `Validacao.objects.create(item=item, ...)` usa o kwarg `item`, mas o campo do modelo é **`item_demanda`**. Ocorre nas duas ações (validar e devolver). | [`validacoes/views.py`](../pac/apps/validacoes/views.py) vs [`validacoes/models.py`](../pac/apps/validacoes/models.py) | O fluxo de validação **lança exceção** ao gravar. |
| B2 | **Duas definições divergentes** de `StatusDemanda`: em [`demandas/models.py`](../pac/apps/demandas/models.py) os valores são minúsculos (`"rascunho"`, sem `VINCULADA_DFD`, com `CANCELADA`); em [`demandas/constants.py`](../pac/apps/demandas/constants.py) são maiúsculos (`"RASCUNHO"`, com `VINCULADA_DFD`, sem `CANCELADA`). As views importam a versão de `models.py`. | `demandas/models.py`, `demandas/constants.py` | Inconsistência de dados; a máquina de transições de `constants.py` não casa com os valores persistidos. |
| B3 | A máquina de estados `pode_transicionar_status()` / `TRANSICOES_STATUS_DEMANDA` **nunca é usada**. As views alteram `status` diretamente, sem validar transição. | `demandas/constants.py`, `demandas/views.py`, `validacoes/views.py` | Transições inválidas não são barradas. |
| B4 | Banco configurado como **SQLite** em `settings.py`, contradizendo README, `.env.example` e `docker-compose.yml` (PostgreSQL). O bloco `DATABASES` ignora as variáveis `DB_*`. | [`config/settings.py`](../pac/config/settings.py) | Ambiente real diverge do planejado; `psycopg2` instalado mas não usado. |
| B5 | `Demanda.save()` é um override **no-op** com comentário indicando que deveria ter sido removido. | `demandas/models.py` | Código morto / confuso. |
| B6 | Endpoints de `usuarios` retornam **JSON sem `@login_required`** e sem checagem de perfil; `ativar`/`desativar` alteram estado via **GET** (sem CSRF/POST). | [`usuarios/views.py`](../pac/apps/usuarios/views.py) | Falha de segurança/controle de acesso (fere RN10). |

---

## 2. Requisitos Funcionais (RF) — status

Referência: seção 10 do PDF.

| RF | Descrição | Estado | Observações |
|---|---|---|---|
| RF01 | Autenticação integrada (login institucional) | ⚠️ | Só login padrão do Django; sem integração institucional (SSO/LDAP). |
| RF02 | Controle de usuários | ⚠️ | Modelo + admin OK; views de gestão são stubs JSON inseguros (B6). |
| RF03 | Gestão de catálogo | ❌ | App `catalogo` sem views/urls e **sem registro no admin**. |
| RF04 | Cadastro de demandas | ✅ | Implementado em `demandas`. |
| RF05 | Inclusão/alteração de itens no catálogo | ❌ | Não há CRUD de `ItemCatalogo`. |
| RF06 | Não duplicidade de itens | ❌ | Nenhuma verificação de item repetido do catálogo. |
| RF08 | Ajuda contextual (tooltips configuráveis) | ❌ | Não há campo/tela para tooltips por item. |
| RF09 | Controle de prazos (calendário do PAC) | ❌ | Sem modelo de calendário/prazo. |
| RF10 | Dashboard gerencial | ❌ | `dashboard` só renderiza `home.html`; sem indicadores. |
| RF11 | Notificações por e-mail | ❌ | Sem backend de e-mail nem envio. |
| RF12 | Gestão de ADMINs | ❌ | Sem tela; papel de ADMIN MASTER não implementado. |
| RF13 | Controle hierárquico | ⚠️ | Acesso por `is_staff`, não pelo campo `perfil`. |
| RF14 | Salvar rascunho | ✅ | Demanda nasce em `RASCUNHO`. |
| RF15 | Enviar solicitação | ✅ | `demanda_enviar`. |
| RF16 | Exportação PDF/XLS | ❌ | Sem biblioteca/rota de exportação. |
| RF17 | Validação por item | ⚠️ | Implementada, mas quebrada por B1. |
| RF18 | Justificativa obrigatória | ⚠️ | Lógica presente na view de devolução (bloqueada por B1). |
| RF19 | Consolidação de itens (agrupar por tipo + somar quantidades) | ⚠️ | Cria DFD a partir de itens validados, mas **sem agrupamento por tipo nem soma de quantidades**. |
| RF20 | Vinculação de DFD (nº) | ⚠️ | Número gravado no DFD; falta propagação (RN17) e status `VINCULADA_DFD`. |
| RF22 | Status por item | ✅ | `ItemDemanda.status` independente (RN19). |
| RF23 | Exportação Excel | ❌ | Não implementada. |
| RF24 | Auditoria completa | ❌ | `LogAuditoria` existe, mas nada grava logs. |
| RF25 | Versionamento (histórico de alteração do formulário) | ❌ | Sem histórico de versões de itens/demandas. |

> Observação: o PDF não lista **RF07** nem **RF21** (lacunas na própria
> numeração original).

---

## 3. Regras de Negócio (RN) — status

Referência: seção 11 do PDF.

| RN | Descrição | Estado | Observações |
|---|---|---|---|
| RN01 | Apenas gestores autorizados solicitam como USUÁRIO | ⚠️ | Depende de `perfil`, hoje não verificado nas views. |
| RN02 | Responsabilidade da unidade solicitante | ✅ | Demanda vincula `unidade` do usuário. |
| RN03 | Prioridade ao item do catálogo | ⚠️ | `item_catalogo` é opcional; sem incentivo/validação de uso preferencial. |
| RN04 | Proibição de duplicidade | ❌ | Não implementado (ver RF06). |
| RN05 | Justificativa obrigatória (devolução/invalidação) | ⚠️ | Regra na view (bloqueada por B1). |
| RN06 | *(sem descrição no PDF)* | ❓ | Requisito sem texto no documento — **precisa de esclarecimento**. |
| RN07 | Governança por grupo (agrupamento de itens) | ⚠️ | Grupo definido no `ItemCatalogo`; agrupamento de consolidação incompleto. |
| RN08 | Respeito aos prazos legais | ❌ | Sem controle de prazo (ver RF09). |
| RN09 | Operação por fases | ❌ | Sem controle de fases/etapas por calendário. |
| RN10 | Permissões por perfil | ⚠️ | Só `is_staff`; perfis ADMIN/ADMIN MASTER não diferenciados. |
| RN11 | ID único por item | ✅ | PK do `ItemDemanda`. |
| RN12 | Vinculação ao DFD | ⚠️ | M2M existe; fluxo incompleto (RF20). |
| RN13 | Vinculação ao processo | ⚠️ | Campo `numero_processo` no DFD; sem fluxo dedicado. |
| RN14 | Transparência (link público) | ⚠️ | Campo `link_publico` no DFD; sem página pública. |
| RN15 | Atualização de status pelo ADMIN | ⚠️ | Ocorre na validação/consolidação (afetada por B1/B3). |
| RN16 | Consolidação apenas de itens validados | ✅ | `dfd_consolidar` filtra `status=VALIDADA`. |
| RN17 | Propagação automática do DFD a todos os itens | ❌ | Não há propagação automática do nº do DFD à tela do USUÁRIO. |
| RN18 | Controle de atraso automático | ❌ | Sem marcação automática de "ATRASADO". |
| RN19 | Independência de status por item | ✅ | `ItemDemanda.status` próprio. |

---

## 4. Módulos / funcionalidades do PDF — status

### 4.1 Módulo do USUÁRIO (seção 6 do PDF)

| Funcionalidade | Estado | Observações |
|---|---|---|
| Inclusão via catálogo (dropdown "Novo Item") | ❌ | `item_catalogo` é campo do form, mas não há seleção que preencha os campos a partir do catálogo. |
| Inclusão manual ("Outros tipos de itens") | ✅ | Preenchimento manual dos campos do item. |
| Campos obrigatórios (quantidade, data prevista, prioridade, justificativas, valor estimado) | ✅ | Presentes no `ItemDemandaForm`. |
| Justificativa de prioridade **só se Alta** | ⚠️ | Campo é sempre obrigatório (modelo `TextField` não-blank); não é condicional à prioridade Alta. |
| Prioridades | ⚠️ | PDF prevê Baixa/Média/Alta; modelo inclui **`CRITICA`** extra. |
| Salvar rascunho / Editar / Enviar | ✅ | Implementado. |
| Botão baixar PDF/XLS (sempre disponível) | ❌ | Não implementado. |
| Não permitir duplicidade | ❌ | Ver RF06/RN04. |
| Soma automática de quantidades por item | ❌ | Não implementado. |
| Tooltips configuráveis | ❌ | Ver RF08. |
| Auto-salvamento | ❌ | Não implementado. |
| Item devolvido: reedição + campo "Observações" + reenviar | ⚠️ | Edição só liberada em `RASCUNHO`; sem fluxo específico de devolução. |

### 4.2 Módulo ADMIN (seções 4.2 e 5 do PDF)

| Funcionalidade | Estado | Observações |
|---|---|---|
| Gerenciar catálogo (cadastro/exclusão de itens, preço por unidade) | ❌ | Sem CRUD; catálogo não registrado no admin. |
| Configurar campos e tooltips | ❌ | Não implementado. |
| Validar / devolver item (com justificativa) | ⚠️ | Implementado, quebrado por B1. |
| Consolidar demandas por item (soma) | ⚠️ | Sem agrupamento/soma (RF19). |
| Vincular DFD ao agrupamento de itens | ⚠️ | Vincula itens ao DFD; sem agrupamento formal. |
| Gerenciar unidades vinculadas | ❌ | App `unidades` sem views/urls e sem admin. |
| Notificação automática ao USUÁRIO por e-mail | ❌ | Ver RF11. |
| Histórico de alteração (auditoria) | ❌ | Ver RF24. |
| Verificação do campo "observação" do USUÁRIO | ⚠️ | Campo `observacao` existe na demanda; sem fluxo de verificação. |

### 4.3 Módulo ADMIN MASTER (seção 4.3 do PDF)

| Funcionalidade | Estado | Observações |
|---|---|---|
| Gerenciar usuários ADMIN | ❌ | Não implementado. |
| Definir grupos de contratação e respectivo ADMIN | ⚠️ | Modelo `GrupoContratacao` existe; sem tela e sem admin registrado. |
| Configurar calendário do PAC (Decreto nº 10.947/2022) | ❌ | Sem modelo/tela de calendário. |
| Envio de e-mail de início de prazo aos gestores | ❌ | Ver RF11. |
| Monitorar execução do sistema | ❌ | Ver dashboard (RF10). |

### 4.4 Dashboard gerencial (seção 8 do PDF)

Todos ❌ (app `dashboard` só renderiza página estática):

- Dashboard ADMIN: % unidades enviaram/não enviaram, valor total estimado,
  valor por unidade, valor por tipo, totais por situação (gráfico), controle de
  prazos, marcação "ATRASADO", alertas por e-mail, exportação Excel.
- Dashboard ADMIN MASTER: visão geral do PAC, ranking por volume de demandas,
  percentuais consolidado/DFD/processo.
- Painel de acompanhamento (futuro): itens com DFD, itens vinculados a processo,
  link para SIPAC.

### 4.5 Rastreabilidade (seção 9 do PDF)

| Item | Estado |
|---|---|
| Identificador único | ✅ (PK) |
| Histórico de alterações | ❌ |
| Unidade solicitante / usuário responsável | ✅ (FKs) |
| Número do DFD | ⚠️ (campo existe; propagação pendente) |
| Número do processo | ⚠️ (campo existe; sem fluxo) |
| Link público | ⚠️ (campo existe; sem página pública) |

---

## 5. Pendências técnicas e de infraestrutura

| # | Pendência | Detalhe |
|---|---|---|
| T1 | Trocar SQLite → PostgreSQL | Ajustar `DATABASES` para usar as variáveis `DB_*` do `.env` (ver B4). |
| T2 | Unificar `StatusDemanda` | Uma única fonte de verdade e adotar a máquina de transições (ver B2/B3). |
| T3 | Camada de serviços | Extrair lógica de consolidação/soma das views (docstring do DFD prevê `services`). |
| T4 | Auditoria automática | Implementar signals/serviço que gravem `LogAuditoria`. |
| T5 | Notificações por e-mail | Configurar backend de e-mail (`EMAIL_*` em settings) e disparos. |
| T6 | Exportações | Adicionar biblioteca(s) para PDF e Excel/XLS. |
| T7 | Registro no Django Admin | Registrar `Unidade`, `GrupoContratacao`, `ItemCatalogo`, `Validacao`, `LogAuditoria` (hoje só `Usuario`, `Demanda`, `DFD`). |
| T8 | Rotas/telas faltantes | `dashboard`, `catalogo`, `unidades`, `grupos`, `auditoria` têm `urls.py` vazio. |
| T9 | Testes automatizados | Todos os `tests.py` estão vazios; sem cobertura. |
| T10 | Permissões por perfil | Substituir `is_staff` por checagem do campo `perfil` (USUÁRIO/ADMIN/ADMIN MASTER). |
| T11 | Integração SIPAC/PGC | Marcada como **FUTURO** no PDF; ainda não iniciada. |
| T12 | Configuração de produção | `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS` e HTTPS para deploy (Render/Supabase). |

---

## 6. Itens que exigem esclarecimento com a equipe/PDF

- **RN06** aparece sem descrição no documento de requisitos (seção 11) — definir
  o texto/regra.
- **RF07** e **RF21** não existem na numeração do PDF — confirmar se é apenas
  lacuna de numeração ou requisitos omitidos.
- **Prioridade "Crítica"** existe no código mas não no PDF (que cita apenas
  Baixa/Média/Alta) — confirmar se deve permanecer.
- **`StatusDemanda.CANCELADA`** existe no modelo e no PDF (seção 7), mas não há
  fluxo de cancelamento implementado — definir quem cancela e quando.

---

## 7. Resumo executivo

| Categoria | ✅ | ⚠️ | ❌ |
|---|---|---|---|
| Requisitos Funcionais (RF) | 4 | 8 | 10 |
| Regras de Negócio (RN) | 4 | 10 | 4 (+1 sem descrição) |
| Bugs conhecidos | — | — | 6 |

**Prioridades sugeridas:**

1. Corrigir os **bugs bloqueantes** B1 (validação) e B2/B3 (status).
2. Alinhar o **banco de dados** (B4/T1) antes de qualquer deploy.
3. Implementar **CRUD de catálogo, unidades e grupos** (RF03/RF05) — hoje não há
   como cadastrar os dados de referência sem `shell`/admin.
4. Implementar **dashboard** (RF10) e **auditoria** (RF24), pilares do
   planejamento.
5. Adicionar **notificações** (RF11) e **exportações** (RF16/RF23).
