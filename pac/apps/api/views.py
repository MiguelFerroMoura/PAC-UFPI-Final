"""
Views da API REST do PAC UFPI.

Expõe autenticação por sessão e os recursos consumidos pelo front-end React.
A regra de negócio replica o fluxo das views server-side originais, agora
sobre endpoints JSON.
"""

from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Sum
from django.middleware.csrf import get_token
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.models import ItemCatalogo
from apps.demandas.constants import pode_transicionar_status
from apps.demandas.models import Demanda, ItemDemanda, StatusDemanda
from apps.dfd.models import DFD
from apps.grupos_contratacao.models import GrupoContratacao
from apps.unidades.models import Unidade
from apps.validacoes.models import TipoAcao, Validacao

from .permissions import IsAdminUserPermission
from .serializers import (
    DemandaSerializer,
    DFDSerializer,
    GrupoContratacaoSerializer,
    ItemCatalogoSerializer,
    ItemDemandaSerializer,
    UnidadeSerializer,
    UsuarioSerializer,
    ValidacaoSerializer,
)


# =============================================================================
# Autenticação (sessão)
# =============================================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def csrf(request):
    """Garante o cookie CSRF para o front-end antes do login."""
    return Response({"detail": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Informe usuário e senha."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Credenciais inválidas."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    login(request, user)
    return Response(UsuarioSerializer(user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UsuarioSerializer(request.user).data)


# =============================================================================
# Recursos de referência
# =============================================================================

class UnidadeViewSet(viewsets.ModelViewSet):
    queryset = Unidade.objects.all()
    serializer_class = UnidadeSerializer


class GrupoContratacaoViewSet(viewsets.ModelViewSet):
    queryset = GrupoContratacao.objects.select_related("unidade_admin").all()
    serializer_class = GrupoContratacaoSerializer


class ItemCatalogoViewSet(viewsets.ModelViewSet):
    queryset = ItemCatalogo.objects.select_related("grupo").all()
    serializer_class = ItemCatalogoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get("ativo") == "true":
            qs = qs.filter(ativo=True)
        return qs


# =============================================================================
# Demandas e itens
# =============================================================================

class DemandaViewSet(viewsets.ModelViewSet):
    serializer_class = DemandaSerializer

    def get_queryset(self):
        qs = (
            Demanda.objects.select_related("unidade", "usuario")
            .prefetch_related("itens")
        )
        user = self.request.user
        # Usuário comum só enxerga as próprias demandas (RN de visibilidade).
        if not user.is_admin_user:
            qs = qs.filter(usuario=user)
        return qs

    def perform_create(self, serializer):
        unidade = getattr(self.request.user, "unidade", None)
        if unidade is None:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "Seu usuário não possui uma unidade vinculada. "
                "Contate o administrador."
            )
        serializer.save(usuario=self.request.user, unidade=unidade)

    def _pode_editar(self, demanda):
        user = self.request.user
        return user.is_admin_user or demanda.usuario_id == user.id

    def update(self, request, *args, **kwargs):
        demanda = self.get_object()
        if not self._pode_editar(demanda):
            return Response(
                {"detail": "Você não tem permissão para editar esta demanda."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if demanda.status != StatusDemanda.RASCUNHO:
            return Response(
                {"detail": "Somente demandas em rascunho podem ser editadas."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["get", "post"])
    def itens(self, request, pk=None):
        demanda = self.get_object()

        if request.method == "GET":
            serializer = ItemDemandaSerializer(demanda.itens.all(), many=True)
            return Response(serializer.data)

        # POST — adiciona um item.
        if not self._pode_editar(demanda):
            return Response(
                {"detail": "Você não tem permissão para adicionar itens."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if demanda.status != StatusDemanda.RASCUNHO:
            return Response(
                {"detail": "Itens só podem ser adicionados em rascunho."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ItemDemandaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(demanda=demanda)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def enviar(self, request, pk=None):
        demanda = self.get_object()
        if not self._pode_editar(demanda):
            return Response(
                {"detail": "Você não tem permissão para enviar esta demanda."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not demanda.itens.exists():
            return Response(
                {"detail": "Adicione pelo menos um item antes de enviar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pode_transicionar_status(demanda.status, StatusDemanda.AGUARDANDO_VALIDACAO):
            return Response(
                {"detail": f"Transição inválida de {demanda.status} para {StatusDemanda.AGUARDANDO_VALIDACAO}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        demanda.status = StatusDemanda.AGUARDANDO_VALIDACAO
        demanda.enviada_em = timezone.now()
        demanda.save(update_fields=["status", "enviada_em", "atualizado_em"])
        demanda.itens.update(status=StatusDemanda.AGUARDANDO_VALIDACAO)
        return Response(DemandaSerializer(demanda).data)


class ItemDemandaViewSet(viewsets.ModelViewSet):
    serializer_class = ItemDemandaSerializer

    def get_queryset(self):
        qs = ItemDemanda.objects.select_related("demanda", "demanda__usuario")
        user = self.request.user
        if not user.is_admin_user:
            qs = qs.filter(demanda__usuario=user)
        return qs

    def _pode_editar(self, item):
        user = self.request.user
        return user.is_admin_user or item.demanda.usuario_id == user.id

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        if not self._pode_editar(item):
            return Response(
                {"detail": "Você não tem permissão para editar este item."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if item.demanda.status != StatusDemanda.RASCUNHO and item.status != StatusDemanda.DEVOLVIDA:
            return Response(
                {"detail": "Itens só podem ser editados em rascunho ou devolvidos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)


# =============================================================================
# Validações
# =============================================================================

class ValidacaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Validacao.objects.select_related("usuario", "item_demanda").all()
    serializer_class = ValidacaoSerializer
    permission_classes = [IsAuthenticated, IsAdminUserPermission]

    @action(detail=False, methods=["get"])
    def pendentes(self, request):
        """Itens aguardando validação (acesso restrito a administradores)."""
        itens = ItemDemanda.objects.filter(
            status=StatusDemanda.AGUARDANDO_VALIDACAO
        ).select_related("demanda", "demanda__unidade", "demanda__usuario")
        return Response(ItemDemandaSerializer(itens, many=True).data)

    @action(detail=False, methods=["post"])
    def decidir(self, request):
        """Valida ou devolve um item de demanda."""
        item_id = request.data.get("item_demanda")
        acao = request.data.get("acao")
        comentario = request.data.get("comentario", "")

        item = ItemDemanda.objects.filter(pk=item_id).first()
        if item is None:
            return Response(
                {"detail": "Item não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if acao == TipoAcao.VALIDADO:
            novo_status = StatusDemanda.VALIDADA
        elif acao == TipoAcao.DEVOLVIDO:
            if not comentario:
                return Response(
                    {"detail": "Comentário é obrigatório para devolução."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            novo_status = StatusDemanda.DEVOLVIDA
        else:
            return Response(
                {"detail": "Ação inválida. Use 'validado' ou 'devolvido'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pode_transicionar_status(item.status, novo_status):
            return Response(
                {"detail": f"Transição de status inválida de {item.status} para {novo_status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.status = novo_status
        item.save(update_fields=["status", "atualizado_em"])
        validacao = Validacao.objects.create(
            item_demanda=item,
            usuario=request.user,
            acao=acao,
            comentario=comentario,
        )
        return Response(
            ValidacaoSerializer(validacao).data, status=status.HTTP_201_CREATED
        )


# =============================================================================
# DFD
# =============================================================================

class DFDViewSet(viewsets.ModelViewSet):
    queryset = (
        DFD.objects.select_related("grupo", "criado_por")
        .prefetch_related("itens_demanda")
        .all()
    )
    serializer_class = DFDSerializer
    permission_classes = [IsAuthenticated, IsAdminUserPermission]

    @action(detail=False, methods=["get"])
    def disponiveis(self, request):
        """Itens validados ainda não vinculados a nenhum DFD."""
        itens = (
            ItemDemanda.objects.filter(status=StatusDemanda.VALIDADA)
            .exclude(dfds__isnull=False)
            .select_related("demanda", "demanda__unidade")
        )
        return Response(ItemDemandaSerializer(itens, many=True).data)

    @action(detail=False, methods=["post"])
    def consolidar(self, request):
        """Cria um DFD a partir de itens validados selecionados."""
        numero = request.data.get("numero")
        grupo_id = request.data.get("grupo")
        item_ids = request.data.get("itens") or []

        if not numero or not grupo_id or not item_ids:
            return Response(
                {"detail": "Informe número, grupo e ao menos um item."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        itens_qs = ItemDemanda.objects.filter(id__in=item_ids)
        for item in itens_qs:
            if not pode_transicionar_status(item.status, StatusDemanda.CONSOLIDADA):
                return Response(
                    {"detail": f"Item #{item.id} em status '{item.status}' não pode ser consolidado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        dfd = DFD.objects.create(
            numero=numero,
            grupo_id=grupo_id,
            criado_por=request.user,
            numero_processo=request.data.get("numero_processo", ""),
            observacao=request.data.get("observacao", ""),
        )
        dfd.itens_demanda.set(item_ids)
        itens_qs.update(status=StatusDemanda.CONSOLIDADA)
        return Response(
            DFDSerializer(dfd).data, status=status.HTTP_201_CREATED
        )


# =============================================================================
# Dashboard
# =============================================================================

class DashboardStatsView(APIView):
    def get(self, request):
        demandas = Demanda.objects
        itens = ItemDemanda.objects

        por_status = {
            row["status"]: row["total"]
            for row in itens.values("status").annotate(total=Count("id"))
        }
        valor_total = itens.aggregate(total=Sum("valor_total"))["total"] or 0

        return Response(
            {
                "total_demandas": demandas.count(),
                "total_itens": itens.count(),
                "itens_por_status": por_status,
                "valor_total_estimado": valor_total,
                "aguardando_validacao": itens.filter(
                    status=StatusDemanda.AGUARDANDO_VALIDACAO
                ).count(),
                "validados": itens.filter(status=StatusDemanda.VALIDADA).count(),
                "consolidados": itens.filter(
                    status=StatusDemanda.CONSOLIDADA
                ).count(),
                "total_dfds": DFD.objects.count(),
            }
        )
