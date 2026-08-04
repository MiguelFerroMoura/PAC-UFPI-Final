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
from apps.demandas.models import Demanda, ItemDemanda, StatusDemanda, StatusItemDemanda
from apps.demandas.services import sincronizar_status_macro_demanda
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

    def test_criar_demanda(self):
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("api:demanda-list"),
            {"ano_referencia": 2027, "observacao": "Teste"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["status"], StatusDemanda.RASCUNHO)

    def test_adicionar_item_a_demanda(self):
        self.client.force_login(self.user)
        demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        resp = self.client.post(
            reverse("api:demanda-itens", kwargs={"pk": demanda.pk}),
            dados_item(),
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(resp.data["valor_total"]), Decimal("3000.00"))
        self.assertEqual(resp.data["status"], StatusItemDemanda.RASCUNHO)

    def test_enviar_demanda_sem_itens_rejeita(self):
        self.client.force_login(self.user)
        demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        resp = self.client.post(
            reverse("api:demanda-enviar", kwargs={"pk": demanda.pk})
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enviar_demanda_com_itens_sucesso(self):
        self.client.force_login(self.user)
        demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        ItemDemanda.objects.create(
            demanda=demanda, tipo="material", nome="Item 1", quantidade=1,
            valor_estimado=Decimal("100"), valor_total=Decimal("100"),
            data_prevista=date(2027, 1, 1),
        )
        resp = self.client.post(
            reverse("api:demanda-enviar", kwargs={"pk": demanda.pk})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        demanda.refresh_from_db()
        self.assertEqual(demanda.status, StatusDemanda.AGUARDANDO_VALIDACAO)

    def test_cancelar_demanda_em_rascunho_pelo_dono(self):
        self.client.force_login(self.user)
        demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )
        ItemDemanda.objects.create(
            demanda=demanda, tipo="material", nome="Item 1", quantidade=1,
            valor_estimado=Decimal("100"), valor_total=Decimal("100"),
            data_prevista=date(2027, 1, 1),
        )
        resp = self.client.post(
            reverse("api:demanda-cancelar", kwargs={"pk": demanda.pk})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        demanda.refresh_from_db()
        self.assertEqual(demanda.status, StatusDemanda.CANCELADA)
        self.assertTrue(all(i.status == StatusItemDemanda.CANCELADA for i in demanda.itens.all()))


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
            status=StatusDemanda.AGUARDANDO_VALIDACAO
        )
        self.item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Cadeira", quantidade=5,
            valor_estimado=Decimal("200"), valor_total=Decimal("1000"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.AGUARDANDO_VALIDACAO
        )

    def test_listar_pendentes_exige_admin(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:validacao-pendentes"))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_pendentes_retorna_itens_aguardando(self):
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
        self.assertEqual(self.item.status, StatusItemDemanda.VALIDADA)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.EM_ANDAMENTO)

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
        self.assertEqual(self.item.status, StatusItemDemanda.DEVOLVIDA)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.EM_ANDAMENTO)

    def test_reenviar_item_devolvido(self):
        self.item.status = StatusItemDemanda.DEVOLVIDA
        self.item.save()
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("api:item-reenviar", kwargs={"pk": self.item.pk})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusItemDemanda.AGUARDANDO_VALIDACAO)


# =============================================================================
# DFD e Consolidação
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
            unidade=self.unidade, usuario=self.user, ano_referencia=2027,
            status=StatusDemanda.EM_ANDAMENTO
        )
        self.item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="X", descricao="d",
            unidade_medida="un", quantidade=1, valor_estimado=Decimal("10"),
            valor_total=Decimal("10"), data_prevista=date(2027, 1, 1),
            prioridade="media", justificativa_prioridade="a",
            justificativa_necessidade="b", indicacao_orcamentaria="c",
            status=StatusItemDemanda.VALIDADA,
        )

    def test_itens_disponiveis(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("api:dfd-disponiveis"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_consolidar_cria_dfd_e_marca_itens_vinculados(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-001", "grupo": self.grupo.pk, "itens": [self.item.pk]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusItemDemanda.VINCULADA_DFD)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.CONCLUIDA)

    def test_consolidar_item_nao_validado_rejeita(self):
        self.item.status = StatusItemDemanda.AGUARDANDO_VALIDACAO
        self.item.save()
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-002", "grupo": self.grupo.pk, "itens": [self.item.pk]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fluxo_completo_ciclo_de_vida(self):
        # 1. Usuário cria demanda em rascunho
        self.client.force_login(self.user)
        demanda_resp = self.client.post(
            reverse("api:demanda-list"),
            {"ano_referencia": 2027, "observacao": "Nova demanda de teste"},
            format="json",
        )
        self.assertEqual(demanda_resp.status_code, status.HTTP_201_CREATED)
        demanda_id = demanda_resp.data["id"]

        # 2. Adiciona item à demanda
        item_resp = self.client.post(
            reverse("api:demanda-itens", kwargs={"pk": demanda_id}),
            {
                "tipo": "material", "nome": "Teclado", "descricao": "USB",
                "unidade_medida": "un", "quantidade": 2, "valor_estimado": "100.00",
                "data_prevista": "2027-03-01", "prioridade": "alta",
                "justificativa_prioridade": "Essencial",
                "justificativa_necessidade": "Substituição",
                "indicacao_orcamentaria": "Recursos próprios",
            },
            format="json",
        )
        self.assertEqual(item_resp.status_code, status.HTTP_201_CREATED)
        item_id = item_resp.data["id"]

        # 3. Usuário envia a demanda
        enviar_resp = self.client.post(reverse("api:demanda-enviar", kwargs={"pk": demanda_id}))
        self.assertEqual(enviar_resp.status_code, status.HTTP_200_OK)

        # 4. Admin valida o item
        self.client.force_login(self.admin)
        valida_resp = self.client.post(
            reverse("api:validacao-decidir"),
            {"item_demanda": item_id, "acao": "validado"},
            format="json",
        )
        self.assertEqual(valida_resp.status_code, status.HTTP_201_CREATED)

        # 5. Admin consolida em DFD
        dfd_resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-2027-01", "grupo": self.grupo.pk, "itens": [item_id]},
            format="json",
        )
        self.assertEqual(dfd_resp.status_code, status.HTTP_201_CREATED)

        # 6. Verifica alteração para VINCULADA_DFD no banco e Demanda CONCLUIDA
        item_obj = ItemDemanda.objects.get(pk=item_id)
        self.assertEqual(item_obj.status, StatusItemDemanda.VINCULADA_DFD)
        demanda_obj = Demanda.objects.get(pk=demanda_id)
        self.assertEqual(demanda_obj.status, StatusDemanda.CONCLUIDA)


# =============================================================================
# Testes do Serviço de Sincronização Macro de Status
# =============================================================================

class SincronizacaoMacroTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(unidade=self.unidade)
        self.demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )

    def test_demanda_sem_itens_eh_rascunho(self):
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.RASCUNHO)

    def test_todos_itens_rascunho_eh_rascunho(self):
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.RASCUNHO,
        )
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.RASCUNHO)

    def test_todos_itens_aguardando_eh_aguardando_validacao(self):
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.AGUARDANDO_VALIDACAO,
        )
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.AGUARDANDO_VALIDACAO)

    def test_itens_mistos_com_devolvido_eh_em_andamento(self):
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.DEVOLVIDA,
        )
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="B", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.AGUARDANDO_VALIDACAO,
        )
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.EM_ANDAMENTO)

    def test_todos_vinculados_eh_concluida(self):
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.VINCULADA_DFD,
        )
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.CONCLUIDA)

    def test_todos_itens_cancelados_eh_cancelada(self):
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.CANCELADA,
        )
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.CANCELADA)

    def test_cancelados_com_ativos_ignora_cancelados(self):
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.CANCELADA,
        )
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="B", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.VINCULADA_DFD,
        )
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.CONCLUIDA)

    def test_demanda_cancelada_nao_reativa_com_sincronizacao(self):
        self.demanda.status = StatusDemanda.CANCELADA
        self.demanda.save()
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.VINCULADA_DFD,
        )
        status_calc = sincronizar_status_macro_demanda(self.demanda)
        self.assertEqual(status_calc, StatusDemanda.CANCELADA)

    def test_idempotencia_da_sincronizacao(self):
        ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.VINCULADA_DFD,
        )
        s1 = sincronizar_status_macro_demanda(self.demanda)
        self.demanda.refresh_from_db()
        st1 = self.demanda.status
        s2 = sincronizar_status_macro_demanda(self.demanda)
        self.demanda.refresh_from_db()
        st2 = self.demanda.status
        self.assertEqual(s1, s2)
        self.assertEqual(st1, st2)
        self.assertEqual(st2, StatusDemanda.CONCLUIDA)

    def test_patch_direto_nao_altera_status_da_demanda(self):
        self.client.force_login(self.user)
        resp = self.client.patch(
            reverse("api:demanda-detail", kwargs={"pk": self.demanda.pk}),
            {"status": StatusDemanda.CONCLUIDA, "observacao": "Tentativa"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.RASCUNHO)


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
