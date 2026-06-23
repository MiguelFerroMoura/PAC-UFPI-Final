from django.db import models


class StatusDemanda(models.TextChoices):
    RASCUNHO = "RASCUNHO", "Rascunho"
    AGUARDANDO_VALIDACAO = "AGUARDANDO_VALIDACAO", "Aguardando validação"
    DEVOLVIDA = "DEVOLVIDA", "Devolvida"
    VALIDADA = "VALIDADA", "Validada"
    CONSOLIDADA = "CONSOLIDADA", "Consolidada"
    VINCULADA_DFD = "VINCULADA_DFD", "Vinculada ao DFD"


TRANSICOES_STATUS_DEMANDA = {
    StatusDemanda.RASCUNHO: [
        StatusDemanda.AGUARDANDO_VALIDACAO,
    ],
    StatusDemanda.AGUARDANDO_VALIDACAO: [
        StatusDemanda.DEVOLVIDA,
        StatusDemanda.VALIDADA,
    ],
    StatusDemanda.DEVOLVIDA: [
        StatusDemanda.RASCUNHO,
        StatusDemanda.AGUARDANDO_VALIDACAO,
    ],
    StatusDemanda.VALIDADA: [
        StatusDemanda.CONSOLIDADA,
    ],
    StatusDemanda.CONSOLIDADA: [
        StatusDemanda.VINCULADA_DFD,
    ],
    StatusDemanda.VINCULADA_DFD: [],
}


def pode_transicionar_status(status_atual, novo_status):
    """
    Verifica se uma demanda pode mudar de um status para outro.
    """
    return novo_status in TRANSICOES_STATUS_DEMANDA.get(status_atual, [])
