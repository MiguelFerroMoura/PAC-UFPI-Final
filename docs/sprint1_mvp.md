# Sprint MVP PAC UFPI

**Período:** 03/08/2026 a 23/08/2026  
**Objetivo:** disponibilizar uma versão do PAC para a Joara validar o fluxo
principal de cadastro, validação, devolução, consolidação e DFD.

## Regra de atualização

- `[ ]` Não iniciado
- `[~]` Em andamento
- `[x]` Concluído
- `[!]` Bloqueado
- Cada pessoa deve atualizar este arquivo ao finalizar uma sessão de trabalho.
- Não iniciar itens opcionais enquanto houver tarefa essencial pendente.

---

# Fluxo que precisa funcionar

- [ ] ADMIN cadastra item no catálogo
- [ ] USUÁRIO cria uma demanda
- [ ] USUÁRIO adiciona itens do catálogo
- [ ] USUÁRIO salva a demanda como rascunho
- [ ] USUÁRIO envia a demanda
- [ ] ADMIN visualiza os itens pendentes
- [ ] ADMIN valida ou devolve cada item
- [ ] USUÁRIO visualiza o motivo da devolução
- [ ] USUÁRIO corrige e reenvia o item
- [ ] ADMIN consolida os itens validados
- [ ] ADMIN vincula os itens a um DFD
- [ ] USUÁRIO visualiza o número do DFD

---

# Caio

## Semana 1 — Fundação

- [x] **P0 — Padronizar os status**
  - [x] Unificar enums e constantes
  - [x] Definir transições permitidas
  - [x] Aplicar transições na API
  - [x] Mantido enums minúsculos (sem necessidade de migração extra)
  - [x] Atualizar o frontend (compatibilidade preservada, 54 testes OK)

- [x] **P0 — Corrigir permissões por perfil**
  - [x] Criar permission class para ADMIN (IsAdminUserPermission)
  - [x] Criar permission class para ADMIN MASTER (IsAdminMasterUserPermission)
  - [x] Encapsular permissões em properties do modelo Usuario (is_admin_user / is_admin_master_user)
  - [x] Proteger endpoints da API
  - [x] Testar acesso com perfil (testes positivos e negativos OK)

- [x] **P0 — Corrigir fluxo de validação**
  - [x] Corrigir bug `item` versus `item_demanda` (views legadas + API)
  - [x] Verificar validação individual
  - [x] Exigir comentário na devolução
  - [x] Garantir registro na tabela `Validacao`

## Semana 2 — Fluxos principais

- [ ] **P0 — Implementar reedição de item devolvido**
  - [ ] Liberar edição somente para item devolvido
  - [ ] Exibir comentário do ADMIN
  - [ ] Implementar reenvio individual
  - [ ] Retornar status para `AGUARDANDO_VALIDACAO`
  - [ ] Preservar histórico das decisões

- [ ] **P0 — Completar consolidação**
  - [ ] Filtrar somente itens validados e sem DFD
  - [ ] Agrupar por item do catálogo
  - [ ] Somar quantidades
  - [ ] Mostrar quantidade por unidade
  - [ ] Criar/vincular DFD
  - [ ] Atualizar status dos itens
  - [ ] Exibir DFD na consulta do usuário

## Semana 3 — Integração e deploy

- [ ] **P0 — Preparar ambiente de homologação**
  - [ ] Configurar variáveis de ambiente
  - [ ] Retirar segredos do código
  - [ ] Configurar `DEBUG=False`
  - [ ] Configurar `ALLOWED_HOSTS`
  - [ ] Configurar CSRF e CORS
  - [ ] Configurar arquivos estáticos
  - [ ] Realizar deploy
  - [ ] Criar usuários de teste

- [ ] **P0 — Testar fluxo completo**
  - [ ] Usuário cria e envia demanda
  - [ ] ADMIN devolve um item
  - [ ] Usuário corrige e reenvia
  - [ ] ADMIN valida
  - [ ] ADMIN consolida
  - [ ] Usuário visualiza o DFD

---

# Miguel

## Semana 1 — Catálogo e formulário

- [ ] **P0 — Registrar modelos no Django Admin**
  - [ ] Unidade
  - [ ] GrupoContratacao
  - [ ] ItemCatalogo
  - [ ] Validacao
  - [ ] DFD
  - [ ] LogAuditoria

- [ ] **P0 — Criar API do catálogo**
  - [ ] Serializer
  - [ ] ViewSet
  - [ ] Rotas
  - [ ] Pesquisa por nome/código
  - [ ] Filtro por grupo
  - [ ] Permissões
  - [ ] Ativar/desativar item

- [ ] **P0 — Criar telas do catálogo**
  - [ ] Listagem
  - [ ] Pesquisa
  - [ ] Cadastro
  - [ ] Edição
  - [ ] Ativação/desativação
  - [ ] Mensagens de sucesso e erro

- [ ] **P0 — Integrar catálogo ao formulário da demanda**
  - [ ] Buscar itens pela API
  - [ ] Selecionar item do catálogo
  - [ ] Autopreencher preço
  - [ ] Calcular valor total
  - [ ] Bloquear duplicidade
  - [ ] Exigir justificativa de prioridade apenas quando alta

## Semana 2 — Validação e interface

- [ ] **P0 — Melhorar tela de validações**
  - [ ] Listar itens pendentes
  - [ ] Filtrar por unidade
  - [ ] Filtrar por grupo
  - [ ] Exibir detalhes do item
  - [ ] Adicionar ação de validar
  - [ ] Adicionar ação de devolver
  - [ ] Exibir mensagens de erro

- [ ] **P0 — Interface do item devolvido**
  - [ ] Exibir badge `DEVOLVIDO`
  - [ ] Mostrar comentário do ADMIN
  - [ ] Reabilitar botão de edição
  - [ ] Mostrar botão de reenvio
  - [ ] Exibir histórico básico

- [ ] **P1 — Interface da consolidação**
  - [ ] Tabela de itens agrupados
  - [ ] Quantidade total
  - [ ] Detalhamento por unidade
  - [ ] Seleção de itens
  - [ ] Formulário do número do DFD
  - [ ] Feedback de consolidação concluída

## Semana 3 — Acabamento

- [ ] **P1 — Melhorar dashboard**
  - [ ] Total de demandas
  - [ ] Total de itens
  - [ ] Valor total
  - [ ] Itens por status
  - [ ] Total de DFDs
  - [ ] Percentual validado
  - [ ] Percentual consolidado

- [ ] **P1 — Revisar frontend**
  - [ ] Estados de carregamento
  - [ ] Estados vazios
  - [ ] Mensagens de erro
  - [ ] Confirmações antes de ações críticas
  - [ ] Padronização de badges
  - [ ] Responsividade básica
  - [ ] Verificar erros no console

- [ ] **P1 — Preparar dados de demonstração**
  - [ ] Unidades
  - [ ] Grupos de contratação
  - [ ] Itens de catálogo
  - [ ] Usuário comum
  - [ ] ADMIN
  - [ ] ADMIN MASTER

---

# Tarefas compartilhadas

- [ ] Revisar mudanças antes de integrar
- [ ] Não enviar arquivos `.env`
- [ ] Não alterar diretamente o banco de produção
- [ ] Testar backend e frontend após integração
- [ ] Atualizar este arquivo diariamente
- [ ] Registrar problemas conhecidos
- [ ] Preparar roteiro para a Joara

---

# Opcionais — apenas se todos os P0 estiverem prontos

- [ ] **P1 — Auditoria mínima**
- [ ] **P1 — Testes automatizados das regras principais**
- [ ] **P2 — Exportação simples em Excel**
- [ ] **P2 — Notificação de devolução por e-mail**
- [ ] **P2 — Calendário básico do PAC**
- [ ] **P2 — Tooltips configuráveis**

---

# Problemas encontrados

Registrar neste formato:

## Problema

**Data:**  
**Encontrado por:**  
**Descrição:**  
**Impacto:**  
**Responsável:**  
**Solução ou decisão:**  

---

# Diário rápido

## 03/08/2026

### Caio

- Feito:
  - Correção do Bug B1 (`item_demanda` nas views de validação).
  - Reutilização direta do enum `StatusDemanda` em `constants.py` e implementação da máquina de estados genérica `pode_transicionar_status`.
  - Encapsulamento de permissões por perfil no modelo `Usuario` (`is_admin_user` / `is_admin_master_user`) e criação das Permission Classes DRF (`IsAdminUserPermission` / `IsAdminMasterUserPermission`).
  - Proteção dos ViewSets (`ValidacaoViewSet`, `DFDViewSet`, etc.) com permissões por perfil e validação de transição de status.
  - Testes automatizados backend (21/21 OK, incluindo testes negativos) e frontend Vitest (54/54 OK).
  - 4 commits independentes realizados.
- Em andamento: Tarefas da Semana 1 concluídas.
- Bloqueio: Nenhum.

### Miguel

# Diário rápido

## 11/08/2026
### Miguel

- Feito:
  - Estrutura e interface do frontend revisadas.
  - Interface das demandas, validações, DFDs e dashboard aprimorada.
  - Componentes visuais e estados de interface padronizados.
  - Responsividade básica implementada/revisada.
- Em andamento:
- Integração completa das telas do catálogo com a API.
- Integração do catálogo ao formulário de demanda.
- Fluxo completo de devolução e reenvio de itens.
- Consolidação e exibição do DFD para o usuário.

- Bloqueio:
- Integração final depende da confirmação das APIs/endpoints disponibilizados pelo backend.

---

# Critério de entrega

O MVP estará pronto quando o fluxo abaixo funcionar no ambiente publicado:

- [ ] Cadastro de catálogo
- [ ] Criação da demanda
- [ ] Inclusão de itens
- [ ] Salvamento como rascunho
- [ ] Envio para validação
- [ ] Validação individual
- [ ] Devolução com justificativa
- [ ] Correção e reenvio
- [ ] Consolidação
- [ ] Vinculação de DFD
- [ ] Visualização do DFD pelo solicitante
