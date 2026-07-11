# Fluxos Principais — PAC UFPI

Mapeamento dos fluxos de negócio do sistema. Fluxos marcados como
**(implementado)**, **(parcial)** ou **(pendente)** conforme o código atual.
As lacunas estão detalhadas em [`05-pendencias.md`](05-pendencias.md).

---

## 1. Fluxo macro do PAC

```txt
USUÁRIO cria demanda
        ↓
USUÁRIO adiciona itens (catálogo ou manual)
        ↓
USUÁRIO envia demanda
        ↓
ADMIN valida ou devolve (por item)
        ↓
Itens validados são consolidados
        ↓
DFD é vinculado (nº do DFD)
        ↓
Dashboard acompanha a execução
```

Este é o fluxo-alvo do planejamento. Abaixo, cada etapa detalhada.

---

## 2. Perfis e responsabilidades

| Perfil | Responsabilidade principal |
|---|---|
| **USUÁRIO** (Gestor da Unidade) | Cadastra e acompanha as demandas da sua unidade |
| **ADMIN** (Unidade Requisitante) | Gerencia catálogo, valida/devolve itens, consolida e vincula DFD |
| **ADMIN MASTER** (PRAD) | Governança geral: gerencia ADMINs, grupos e calendário do PAC |

> No código atual, a distinção de acesso é feita por `request.user.is_staff`
> (não pelo campo `perfil`). Ver [`05-pendencias.md`](05-pendencias.md).

---

## 3. Ciclo de vida (status) da demanda / item

Estados definidos em `demandas.StatusDemanda`:

```
RASCUNHO ──► AGUARDANDO_VALIDACAO ──► VALIDADA ──► CONSOLIDADA (no DFD)
                    │
                    └──► DEVOLVIDA ──► (volta a edição)

                    (CANCELADA — estado terminal)
```

Transições formais previstas em
[`demandas/constants.py`](../pac/apps/demandas/constants.py):

```
RASCUNHO             → AGUARDANDO_VALIDACAO
AGUARDANDO_VALIDACAO → DEVOLVIDA | VALIDADA
DEVOLVIDA            → RASCUNHO | AGUARDANDO_VALIDACAO
VALIDADA             → CONSOLIDADA
CONSOLIDADA          → VINCULADA_DFD
VINCULADA_DFD        → (terminal)
```

> Cada `ItemDemanda` tem **status próprio** (RN19), permitindo que itens da
> mesma demanda estejam em estágios diferentes.

---

## 4. Fluxo: cadastro e envio de demanda — USUÁRIO **(implementado)**

Arquivos: [`demandas/views.py`](../pac/apps/demandas/views.py),
[`demandas/forms.py`](../pac/apps/demandas/forms.py).

```txt
1. Login  ──►  /login/  (sessão)
2. /demandas/nova/         demanda_create
      • cria Demanda em RASCUNHO
      • usuário = request.user
      • unidade = user.unidade (erro se não houver)
3. /demandas/<pk>/         demanda_detail
4. /demandas/<pk>/itens/novo/   item_create
      • adiciona ItemDemanda (status RASCUNHO)
      • valor_total = quantidade × valor_estimado (calculado na view)
5. (opcional) item_update / demanda_update
      • permitidos SOMENTE enquanto a demanda está em RASCUNHO
6. /demandas/<pk>/enviar/   demanda_enviar
      • exige ≥ 1 item
      • Demanda → AGUARDANDO_VALIDACAO (registra enviada_em)
      • Itens   → AGUARDANDO_VALIDACAO (em lote)
```

Regras de permissão aplicadas: usuário não-staff só vê/edita as **próprias**
demandas (`qs.filter(usuario=request.user)` e checagens em cada view).

**Diagrama de estados nesta etapa:**

```
[criar] RASCUNHO ──(adicionar itens)──► RASCUNHO ──(enviar)──► AGUARDANDO_VALIDACAO
```

---

## 5. Fluxo: validação de itens — ADMIN **(parcial / com defeito)**

Arquivos: [`validacoes/views.py`](../pac/apps/validacoes/views.py),
[`validacoes/models.py`](../pac/apps/validacoes/models.py).

```txt
1. /validacoes/pendentes/            lista_pendentes
      • lista ItemDemanda com status AGUARDANDO_VALIDACAO
      • acesso restrito a is_staff
2. /validacoes/item/<pk>/decidir/    validar_item
      • Ação "validar":  Item → VALIDADA  + registro Validacao(VALIDADO)
      • Ação "devolver": Item → DEVOLVIDA + registro Validacao(DEVOLVIDO)
                         (comentário/justificativa OBRIGATÓRIO — RN05)
```

Cada decisão gera um registro `Validacao` para rastreabilidade (RF17 —
validação por item).

> **Defeito conhecido:** a view cria `Validacao.objects.create(item=item, ...)`,
> mas o campo do modelo se chama `item_demanda`. Isso lança erro em tempo de
> execução. Registrado em [`05-pendencias.md`](05-pendencias.md).

**Diagrama de estados nesta etapa:**

```
AGUARDANDO_VALIDACAO ──(validar)──►  VALIDADA
                     └─(devolver)──► DEVOLVIDA
```

---

## 6. Fluxo: item devolvido — USUÁRIO **(parcial)**

Previsto no planejamento: tela de edição reabilitada, campo "Observações" e
botão de reenvio.

```txt
Item DEVOLVIDA ──► usuário corrige ──► reenvia ──► AGUARDANDO_VALIDACAO
```

> No código atual, `demanda_update`/`item_update` só permitem edição quando a
> **demanda** está em `RASCUNHO`. O fluxo específico de reedição de item
> devolvido (com campo "Observação" e reenvio direto) ainda não está
> implementado. Ver [`05-pendencias.md`](05-pendencias.md).

---

## 7. Fluxo: consolidação e vínculo de DFD — ADMIN **(parcial)**

Arquivos: [`dfd/views.py`](../pac/apps/dfd/views.py),
[`dfd/models.py`](../pac/apps/dfd/models.py).

```txt
1. /dfds/consolidar/     dfd_consolidar
      • lista ItemDemanda VALIDADA ainda sem DFD
      • seleciona itens + grupo + número do DFD
      • cria DFD, associa itens (M2M)
      • Itens selecionados → CONSOLIDADA
2. /dfds/               dfd_list      (lista DFDs)
3. /dfds/<pk>/          dfd_detail    (detalhe + soma dos valores dos itens)
```

Regras atendidas: consolidação **apenas de itens validados** (RN16); vínculo do
número do DFD aos itens (RF20).

> Pendências: **agrupamento por tipo de item + soma de quantidades** (RF19), e a
> **propagação automática do nº do DFD** para a tela do USUÁRIO (RN17). Ver
> [`05-pendencias.md`](05-pendencias.md).

**Diagrama de estados nesta etapa:**

```
VALIDADA ──(consolidar em DFD)──► CONSOLIDADA ──(planejado)──► VINCULADA_DFD
```

---

## 8. Fluxo: acompanhamento gerencial — DASHBOARD **(pendente)**

```txt
Dados das demandas/itens ──► indicadores ──► Dashboard (ADMIN / ADMIN MASTER)
```

Previsto no planejamento (RF10):

- **ADMIN**: % de unidades que enviaram/não enviaram, valores estimados por
  unidade e por tipo, quantitativos por situação, controle de prazos, exportação
  Excel.
- **ADMIN MASTER**: visão geral do PAC, ranking por volume de demandas,
  percentuais consolidado/DFD/processo.

> No código atual, `dashboard.views.home` apenas renderiza `home.html` estático;
> não há indicadores nem rotas de dashboard. Ver
> [`05-pendencias.md`](05-pendencias.md).

---

## 9. Fluxo: administração/governança — ADMIN MASTER **(pendente)**

Previsto: gerenciar usuários ADMIN, definir grupos de contratação e respectivos
ADMINs, configurar o calendário do PAC (prazos conforme Decreto nº 10.947/2022)
e disparar e-mails de início de prazo.

> Hoje, o cadastro de `Unidade`, `GrupoContratacao` e `ItemCatalogo` só é
> possível via Django Admin — e mesmo assim **apenas** para os modelos
> registrados no admin (`Usuario`, `Demanda`, `DFD`). Ver
> [`05-pendencias.md`](05-pendencias.md).

---

## 10. Rastreabilidade e auditoria **(pendente)**

Previsto (RF24/RN11): cada item com identificador único, histórico de
alterações, unidade solicitante, responsável, nº do DFD, nº do processo e link
público.

> O modelo `LogAuditoria` existe, mas nenhum código escreve registros de
> auditoria. Ver [`05-pendencias.md`](05-pendencias.md).

---

## 11. Resumo do estado dos fluxos

| Fluxo | Estado |
|---|---|
| Cadastro e envio de demanda (USUÁRIO) | ✅ Implementado |
| Validação/devolução por item (ADMIN) | ⚠️ Parcial (defeito em `Validacao`) |
| Reedição de item devolvido | ⚠️ Parcial |
| Consolidação + vínculo de DFD | ⚠️ Parcial (sem agrupamento/soma e propagação) |
| Dashboard gerencial | ❌ Pendente |
| Governança (ADMIN MASTER) | ❌ Pendente |
| Auditoria/rastreabilidade | ❌ Pendente |
| Notificações por e-mail | ❌ Pendente |
| Exportação PDF/XLS/Excel | ❌ Pendente |
