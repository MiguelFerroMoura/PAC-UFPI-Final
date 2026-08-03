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

- [ ] **P0 — Padronizar os status**
  - [ ] Unificar enums e constantes
  - [ ] Definir transições permitidas
  - [ ] Aplicar transições na API
  - [ ] Criar migração para dados existentes
  - [ ] Atualizar o frontend

- [ ] **P0 — Corrigir permissões por perfil**
  - [ ] Criar permission class para ADMIN
  - [ ] Criar permission class para ADMIN MASTER
  - [ ] Remover dependência indevida de `is_staff`
  - [ ] Proteger endpoints
  - [ ] Testar acesso com os três perfis

- [ ] **P0 — Corrigir fluxo de validação**
  - [ ] Corrigir bug `item` versus `item_demanda`
  - [ ] Verificar validação individual
  - [ ] Exigir comentário na devolução
  - [ ] Garantir registro na tabela `Validacao`

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
- Em andamento:
- Bloqueio:

### Miguel

- Feito:
- Em andamento:
- Bloqueio:

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