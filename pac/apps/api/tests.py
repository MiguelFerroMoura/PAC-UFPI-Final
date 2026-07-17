"""
Testes da API REST do PAC UFPI.

Cobrem autenticação por sessão e os principais fluxos de negócio expostos
pela API consumida pelo front-end React.
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.models import ItemCatalogo
from apps.demandas.models import Demanda, ItemDemanda, StatusDemanda
from apps.grupos_contratacao.models import GrupoContratacao
from apps.unidades.models import Unidade

Usuario = get_user_model()


def criar_unidade(sigla="STI"):
    return Unidade.objects.create(
        nome=f"Unidade {sigla}", sigla=sigla, codigo=f"COD-{sigla}"
    )


def criar_usuario(username="ana", unidade=None, is_staff=False, perfil="usuario"):
    return Usuario.objects.create_user(
        username=username,
        password="senha12345",
        email=f"{username}@ufpi.edu.br",
        siape=f"SIAPE-{username}",
        unidade=unidade,
        is_staff=is_staff,
        perfil=perfil,
    )


def dados_item(**overrides):
    dados = {
        "tipo": "material",
        "nome": "Notebook",
        "descricao": "Notebook institucional",
        "unidade_medida": "unidade",
        "quantidade": 2,
        "valor_estimado": "1500.00",
        "data_prevista": date(2027, 1, 1).isoformat(),
        "prioridade": "media",
        "justificativa_prioridade": "Necessário",
        "justificativa_necessidade": "Trabalho",
        "indicacao_orcamentaria": "Orçamento X",
    }
    dados.update(overrides)
    return dados


# =============================================================================
# Autenticação
# =============================================================================

class AutenticacaoTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(unidade=self.unidade)

    def test_login_com_credenciais_validas(self):
        resp = self.client.post(
            reverse("api:login"),
            {"username": "ana", "password": "senha12345"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "ana")

    def test_login_com_credenciais_invalidas(self):
        resp = self.client.post(
            reverse("api:login"),
            {"username": "ana", "password": "errada"},
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_exige_autenticacao(self):
        resp = self.client.get(reverse("api:me"))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_retorna_usuario_logado(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:me"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "ana")


# =============================================================================
# Demandas
# =============================================================================

class DemandaTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(unidade=self.unidade)
        self.outro = criar_usuario(username="bob", unidade=self.unidade)

    def test_criar_demanda_vincula_usuario_e_unidade(self):
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("api:demanda-list"), {"ano_referencia": 2027}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["usuario"], self.user.id)
        self.assertEqual(resp.data["unidade"], self.unidade.id)
        self.assertEqual(resp.data["status"], StatusDemanda.RASCUNHO)

    def test_criar_demanda_sem_unidade_falha(self):
        sem_unidade = criar_usuario(username="semunid")
        self.client.force_login(sem_unidade)
        resp = self.client.post(
            reverse("api:demanda-list"), {"ano_referencia": 2027}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_usuario_comum_ve_apenas_suas_demandas(self):
        Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        Demanda.objects.create(
            unidade=self.unidade, usuario=self.outro, ano_referencia=2027
        )
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:demanda-list"))
        self.assertEqual(resp.data["count"], 1)

    def test_adicionar_item_calcula_valor_total(self):
        demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("api:demanda-itens", args=[demanda.pk]), dados_item()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(resp.data["valor_total"]), Decimal("3000.00"))

    def test_enviar_sem_itens_falha(self):
        demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        self.client.force_login(self.user)
        resp = self.client.post(reverse("api:demanda-enviar", args=[demanda.pk]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enviar_com_itens_muda_status(self):
        demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        ItemDemanda.objects.create(
            demanda=demanda, tipo="material", nome="X", descricao="d",
            unidade_medida="un", quantidade=1, valor_estimado=Decimal("10"),
            valor_total=Decimal("10"), data_prevista=date(2027, 1, 1),
            prioridade="media", justificativa_prioridade="a",
            justificativa_necessidade="b", indicacao_orcamentaria="c",
        )
        self.client.force_login(self.user)
        resp = self.client.post(reverse("api:demanda-enviar", args=[demanda.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], StatusDemanda.AGUARDANDO_VALIDACAO)


# =============================================================================
# Validações
# =============================================================================

class ValidacaoTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(unidade=self.unidade)
        self.admin = criar_usuario(username="admin", is_staff=True, perfil="admin")
        self.demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027,
            status=StatusDemanda.AGUARDANDO_VALIDACAO,
        )
        self.item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="X", descricao="d",
            unidade_medida="un", quantidade=1, valor_estimado=Decimal("10"),
            valor_total=Decimal("10"), data_prevista=date(2027, 1, 1),
            prioridade="media", justificativa_prioridade="a",
            justificativa_necessidade="b", indicacao_orcamentaria="c",
            status=StatusDemanda.AGUARDANDO_VALIDACAO,
        )

    def test_pendentes_restrito_a_admin(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:validacao-pendentes"))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_pendentes_lista_itens_aguardando(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("api:validacao-pendentes"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_validar_item(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:validacao-decidir"),
            {"item_demanda": self.item.pk, "acao": "validado"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusDemanda.VALIDADA)

    def test_devolver_exige_comentario(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:validacao-decidir"),
            {"item_demanda": self.item.pk, "acao": "devolvido"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_devolver_com_comentario(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:validacao-decidir"),
            {
                "item_demanda": self.item.pk,
                "acao": "devolvido",
                "comentario": "Ajustar valor",
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusDemanda.DEVOLVIDA)


# =============================================================================
# DFD
# =============================================================================

class DFDTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(unidade=self.unidade)
        self.admin = criar_usuario(username="admin", is_staff=True, perfil="admin")
        self.grupo = GrupoContratacao.objects.create(
            nome="TIC", unidade_admin=self.unidade
        )
        self.demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        self.item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="X", descricao="d",
            unidade_medida="un", quantidade=1, valor_estimado=Decimal("10"),
            valor_total=Decimal("10"), data_prevista=date(2027, 1, 1),
            prioridade="media", justificativa_prioridade="a",
            justificativa_necessidade="b", indicacao_orcamentaria="c",
            status=StatusDemanda.VALIDADA,
        )

    def test_itens_disponiveis(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("api:dfd-disponiveis"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_consolidar_cria_dfd_e_marca_itens(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-001", "grupo": self.grupo.pk, "itens": [self.item.pk]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusDemanda.CONSOLIDADA)
        self.assertEqual(Decimal(resp.data["total"]), Decimal("10"))


# =============================================================================
# Catálogo e Dashboard
# =============================================================================

class CatalogoDashboardTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(unidade=self.unidade)
        self.grupo = GrupoContratacao.objects.create(
            nome="TIC", unidade_admin=self.unidade
        )
        ItemCatalogo.objects.create(
            tipo="material", nome="Mouse", grupo=self.grupo,
            unidade_medida="un", valor_estimado=Decimal("50"),
        )

    def test_listar_catalogo(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:catalogo-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_dashboard_stats(self):
        Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:dashboard-stats"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["total_demandas"], 1)
        self.assertIn("itens_por_status", resp.data)
