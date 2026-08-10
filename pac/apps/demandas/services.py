from apps.demandas.models import Demanda, StatusDemanda, StatusItemDemanda


def sincronizar_status_macro_demanda(demanda: Demanda) -> str:
    """
    Calcula e atualiza de forma determinística e idempotente o status macro da Demanda
    com base no estado dos seus itens.

    Precedência Estrita:
    1. Demanda cancelada explicitamente não é reativada por recálculo.
    2. Demanda sem itens -> rascunho.
    3. Todos os itens cancelados -> cancelada.
    4. Todos os itens ativos em rascunho -> rascunho.
    5. Todos os itens ativos em aguardando_validacao -> aguardando_validacao.
    6. Todos os itens ativos em vinculada_dfd (ou consolidada legada) -> concluida.
    7. Qualquer outra combinação de itens ativos -> em_andamento.

    Assunção: A camada chamadora já abriu transação (transaction.atomic)
    e adquiriu bloqueio (select_for_update).
    Não abre transação própria nem faz select_for_update.
    """
    if demanda.status == StatusDemanda.CANCELADA:
        return StatusDemanda.CANCELADA

    itens = list(demanda.itens.all())
    if not itens:
        novo_status = StatusDemanda.RASCUNHO
    else:
        ativos = [i for i in itens if i.status != StatusItemDemanda.CANCELADA]
        if not ativos:
            novo_status = StatusDemanda.CANCELADA
        elif all(i.status == StatusItemDemanda.RASCUNHO for i in ativos):
            novo_status = StatusDemanda.RASCUNHO
        elif all(i.status == StatusItemDemanda.AGUARDANDO_VALIDACAO for i in ativos):
            novo_status = StatusDemanda.AGUARDANDO_VALIDACAO
        elif all(i.status in [StatusItemDemanda.VINCULADA_DFD, "consolidada"] for i in ativos):
            novo_status = StatusDemanda.CONCLUIDA
        else:
            novo_status = StatusDemanda.EM_ANDAMENTO

    if demanda.status != novo_status:
        demanda.status = novo_status
        demanda.save(update_fields=["status", "atualizado_em"])

    return demanda.status
