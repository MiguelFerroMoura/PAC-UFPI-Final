from apps.demandas.models import StatusDemanda


TRANSICOES_STATUS = {
    StatusDemanda.RASCUNHO: {
        StatusDemanda.AGUARDANDO_VALIDACAO,
    },
    StatusDemanda.AGUARDANDO_VALIDACAO: {
        StatusDemanda.DEVOLVIDA,
        StatusDemanda.VALIDADA,
    },
    StatusDemanda.DEVOLVIDA: {
        StatusDemanda.RASCUNHO,
        StatusDemanda.AGUARDANDO_VALIDACAO,
    },
    StatusDemanda.VALIDADA: {
        StatusDemanda.CONSOLIDADA,
    },
    StatusDemanda.CONSOLIDADA: {
        StatusDemanda.VINCULADA_DFD,
    },
    StatusDemanda.VINCULADA_DFD: set(),
    StatusDemanda.CANCELADA: set(),
}


def pode_transicionar_status(status_atual, novo_status):
    """
    Verifica genericamente se a transição entre status_atual e novo_status é válida.
    """
    return novo_status in TRANSICOES_STATUS.get(status_atual, set())
