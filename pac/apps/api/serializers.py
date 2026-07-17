"""
Serializers da API REST do PAC UFPI.

Convertem os modelos do Django em JSON consumido pelo front-end React.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.catalogo.models import ItemCatalogo
from apps.demandas.models import Demanda, ItemDemanda, StatusDemanda
from apps.dfd.models import DFD
from apps.grupos_contratacao.models import GrupoContratacao
from apps.unidades.models import Unidade
from apps.validacoes.models import Validacao

Usuario = get_user_model()


# =============================================================================
# Usuários / Autenticação
# =============================================================================

class UsuarioSerializer(serializers.ModelSerializer):
    nome_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id", "username", "first_name", "last_name", "nome_completo",
            "email", "siape", "perfil", "unidade", "is_staff",
        ]

    def get_nome_completo(self, obj):
        return obj.get_full_name() or obj.username


# =============================================================================
# Unidades / Grupos / Catálogo
# =============================================================================

class UnidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ["id", "nome", "sigla", "codigo", "ativo"]


class GrupoContratacaoSerializer(serializers.ModelSerializer):
    unidade_admin_sigla = serializers.CharField(
        source="unidade_admin.sigla", read_only=True
    )

    class Meta:
        model = GrupoContratacao
        fields = [
            "id", "nome", "descricao", "unidade_admin",
            "unidade_admin_sigla", "ativo",
        ]


class ItemCatalogoSerializer(serializers.ModelSerializer):
    grupo_nome = serializers.CharField(source="grupo.nome", read_only=True)

    class Meta:
        model = ItemCatalogo
        fields = [
            "id", "tipo", "nome", "descricao", "codigo_catmat_catser",
            "grupo", "grupo_nome", "unidade_medida", "valor_estimado", "ativo",
        ]


# =============================================================================
# Demandas e itens
# =============================================================================

class ItemDemandaSerializer(serializers.ModelSerializer):
    # valor_total é calculado no back-end (quantidade × valor_estimado).
    valor_total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ItemDemanda
        fields = [
            "id", "demanda", "item_catalogo", "tipo", "nome", "descricao",
            "unidade_medida", "quantidade", "valor_estimado", "valor_total",
            "data_prevista", "prioridade", "justificativa_prioridade",
            "justificativa_necessidade", "indicacao_orcamentaria",
            "status", "status_display",
        ]
        read_only_fields = ["demanda", "status"]

    def create(self, validated_data):
        validated_data["valor_total"] = (
            validated_data["quantidade"] * validated_data["valor_estimado"]
        )
        validated_data["status"] = StatusDemanda.RASCUNHO
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.valor_total = instance.quantidade * instance.valor_estimado
        instance.save(update_fields=["valor_total", "atualizado_em"])
        return instance


class DemandaSerializer(serializers.ModelSerializer):
    itens = ItemDemandaSerializer(many=True, read_only=True)
    unidade_sigla = serializers.CharField(source="unidade.sigla", read_only=True)
    usuario_nome = serializers.CharField(source="usuario.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    valor_total = serializers.SerializerMethodField()

    class Meta:
        model = Demanda
        fields = [
            "id", "unidade", "unidade_sigla", "usuario", "usuario_nome",
            "ano_referencia", "status", "status_display", "observacao",
            "enviada_em", "criado_em", "atualizado_em", "itens", "valor_total",
        ]
        read_only_fields = ["unidade", "usuario", "status", "enviada_em"]

    def get_valor_total(self, obj):
        return sum((item.valor_total for item in obj.itens.all()), start=0)


# =============================================================================
# Validações
# =============================================================================

class ValidacaoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(
        source="usuario.get_full_name", read_only=True
    )
    acao_display = serializers.CharField(source="get_acao_display", read_only=True)

    class Meta:
        model = Validacao
        fields = [
            "id", "item_demanda", "usuario", "usuario_nome",
            "acao", "acao_display", "comentario", "criado_em",
        ]
        read_only_fields = ["usuario"]


# =============================================================================
# DFD
# =============================================================================

class DFDSerializer(serializers.ModelSerializer):
    grupo_nome = serializers.CharField(source="grupo.nome", read_only=True)
    criado_por_nome = serializers.CharField(
        source="criado_por.get_full_name", read_only=True
    )
    itens = ItemDemandaSerializer(
        source="itens_demanda", many=True, read_only=True
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = DFD
        fields = [
            "id", "numero", "grupo", "grupo_nome", "criado_por",
            "criado_por_nome", "numero_processo", "link_publico",
            "observacao", "criado_em", "atualizado_em", "itens", "total",
        ]
        read_only_fields = ["criado_por"]

    def get_total(self, obj):
        return sum((item.valor_total for item in obj.itens_demanda.all()), start=0)
