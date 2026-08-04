"""
Testes da API REST do PAC UFPI.

Cobrem autenticação por sessão e os principais fluxos de negócio expostos
pela API consumida pelo front-end React.
"""

from datetime import date
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.models import ItemCatalogo
from apps.demandas.models import Demanda, ItemDemanda, StatusDemanda, StatusItemDemanda
from apps.demandas.services import sincronizar_status_macro_demanda
from apps.dfd.models import DFD
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
            data_prevista=date(2027, 1, 1), justificativa_necessidade="Uso necessário",
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
        self.item.justificativa_necessidade = "Justificativa válida"
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

    def test_consolidacao_reverte_todas_as_escritas_em_falha_intermediaria(self):
        dfd_count_inicial = DFD.objects.count()
        self.client.force_login(self.admin)
        with mock.patch("apps.api.views.sincronizar_status_macro_demanda", side_effect=RuntimeError("Falha simulada")):
            with self.assertRaises(RuntimeError):
                self.client.post(
                    reverse("api:dfd-consolidar"),
                    {"numero": "DFD-FAIL", "grupo": self.grupo.pk, "itens": [self.item.pk]},
                    format="json",
                )
        self.assertFalse(DFD.objects.filter(numero="DFD-FAIL").exists())
        self.assertEqual(DFD.objects.count(), dfd_count_inicial)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusItemDemanda.VALIDADA)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.EM_ANDAMENTO)

    def test_consolidar_itens_de_multiplas_demandas_sincroniza_todas(self):
        demanda_b = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027,
            status=StatusDemanda.EM_ANDAMENTO
        )
        item_b = ItemDemanda.objects.create(
            demanda=demanda_b, tipo="material", nome="Y", descricao="d2",
            unidade_medida="un", quantidade=1, valor_estimado=Decimal("20"),
            valor_total=Decimal("20"), data_prevista=date(2027, 1, 1),
            prioridade="media", justificativa_prioridade="a",
            justificativa_necessidade="b", indicacao_orcamentaria="c",
            status=StatusItemDemanda.VALIDADA,
        )
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-MULTI", "grupo": self.grupo.pk, "itens": [self.item.pk, item_b.pk]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DFD.objects.filter(numero="DFD-MULTI").count(), 1)
        self.item.refresh_from_db()
        item_b.refresh_from_db()
        self.assertEqual(self.item.status, StatusItemDemanda.VINCULADA_DFD)
        self.assertEqual(item_b.status, StatusItemDemanda.VINCULADA_DFD)
        self.demanda.refresh_from_db()
        demanda_b.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.CONCLUIDA)
        self.assertEqual(demanda_b.status, StatusDemanda.CONCLUIDA)

    def test_consolidar_rejeita_id_inexistente(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-BAD-ID", "grupo": self.grupo.pk, "itens": [999999]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DFD.objects.filter(numero="DFD-BAD-ID").count(), 0)

    def test_consolidar_desduplica_ids_repetidos(self):
        # A desduplicação automática da lista de itens na consolidação é intencional para o MVP.
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-DUP", "grupo": self.grupo.pk, "itens": [self.item.pk, self.item.pk]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        dfd = DFD.objects.get(numero="DFD-DUP")
        self.assertEqual(dfd.itens_demanda.count(), 1)

    def test_consolidar_rejeita_item_ja_vinculado(self):
        self.item.status = StatusItemDemanda.VINCULADA_DFD
        self.item.save()
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-ALREADY", "grupo": self.grupo.pk, "itens": [self.item.pk]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DFD.objects.filter(numero="DFD-ALREADY").count(), 0)

    def test_consolidar_rejeita_item_de_demanda_concluida(self):
        self.demanda.status = StatusDemanda.CONCLUIDA
        self.demanda.save()
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("api:dfd-consolidar"),
            {"numero": "DFD-CLOSED", "grupo": self.grupo.pk, "itens": [self.item.pk]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(DFD.objects.filter(numero="DFD-CLOSED").count(), 0)

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

    def test_patch_direto_nao_altera_status_do_item(self):
        item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Item A", quantidade=1,
            valor_estimado=Decimal("10"), valor_total=Decimal("10"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.RASCUNHO,
        )
        self.client.force_login(self.user)
        resp = self.client.patch(
            reverse("api:item-detail", kwargs={"pk": item.pk}),
            {"status": StatusItemDemanda.VALIDADA},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.status, StatusItemDemanda.RASCUNHO)

    def test_alterar_demanda_concluida_rejeita(self):
        self.demanda.status = StatusDemanda.CONCLUIDA
        self.demanda.save()
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("api:demanda-itens", kwargs={"pk": self.demanda.pk}),
            dados_item(),
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)


# =============================================================================
# Server-Side Integration
# =============================================================================

class ServerSideIntegrationTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(unidade=self.unidade)
        self.admin = criar_usuario(username="admin", is_staff=True, perfil="admin")
        self.demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027
        )

    def test_server_side_envio_e_validacao(self):
        item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Monitor", quantidade=1,
            valor_estimado=Decimal("500"), valor_total=Decimal("500"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.RASCUNHO,
            justificativa_necessidade="Uso necessário",
        )
        self.client.force_login(self.user)
        resp = self.client.post(reverse("demandas:enviar", kwargs={"pk": self.demanda.pk}))
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.AGUARDANDO_VALIDACAO)

        self.client.force_login(self.admin)
        val_resp = self.client.post(
            reverse("validacoes:validar_item", kwargs={"item_pk": item.pk}),
            {"acao": "aprovar"},
        )
        self.assertEqual(val_resp.status_code, status.HTTP_302_FOUND)
        item.refresh_from_db()
        self.assertEqual(item.status, StatusItemDemanda.VALIDADA)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.EM_ANDAMENTO)

    def test_server_side_item_reenviar(self):
        from apps.validacoes.models import Validacao, TipoAcao
        item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Teclado", quantidade=1,
            valor_estimado=Decimal("100"), valor_total=Decimal("100"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.DEVOLVIDA,
            justificativa_necessidade="Necessário",
        )
        Validacao.objects.create(item_demanda=item, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario="Corrigir descrição")

        self.client.force_login(self.user)
        resp = self.client.post(reverse("demandas:item_reenviar", kwargs={"pk": item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        item.refresh_from_db()
        self.assertEqual(item.status, StatusItemDemanda.AGUARDANDO_VALIDACAO)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.AGUARDANDO_VALIDACAO)

    def test_server_side_item_reenviar_sem_csrf_rejeita(self):
        from django.test import Client
        from apps.validacoes.models import Validacao, TipoAcao
        csrf_client = Client(enforce_csrf_checks=True)
        item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Mouse CSRF", quantidade=1,
            valor_estimado=Decimal("50"), valor_total=Decimal("50"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.DEVOLVIDA,
            justificativa_necessidade="Necessário",
        )
        Validacao.objects.create(item_demanda=item, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario="Devolvido")
        csrf_client.force_login(self.user)

        resp = csrf_client.post(reverse("demandas:item_reenviar", kwargs={"pk": item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_server_side_item_reenviar_com_csrf_sucesso(self):
        from django.test import Client
        from apps.validacoes.models import Validacao, TipoAcao
        csrf_client = Client(enforce_csrf_checks=True)
        item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Mouse CSRF Valid", quantidade=1,
            valor_estimado=Decimal("50"), valor_total=Decimal("50"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.DEVOLVIDA,
            justificativa_necessidade="Necessário",
        )
        Validacao.objects.create(item_demanda=item, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario="Devolvido")
        csrf_client.force_login(self.user)

        get_resp = csrf_client.get(reverse("demandas:detalhe", kwargs={"pk": self.demanda.pk}))
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        csrf_token = csrf_client.cookies["csrftoken"].value

        resp = csrf_client.post(
            reverse("demandas:item_reenviar", kwargs={"pk": item.pk}),
            {"csrfmiddlewaretoken": csrf_token},
        )
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        item.refresh_from_db()
        self.assertEqual(item.status, StatusItemDemanda.AGUARDANDO_VALIDACAO)


class ItemDevolvidoCorrecaoTests(APITestCase):
    def setUp(self):
        self.unidade = criar_unidade()
        self.user = criar_usuario(username="solicitante", unidade=self.unidade)
        self.outro_user = criar_usuario(username="outro", unidade=self.unidade)
        self.admin = criar_usuario(username="admin_test", is_staff=True, perfil="admin")
        self.demanda = Demanda.objects.create(
            unidade=self.unidade, usuario=self.user, ano_referencia=2027,
            status=StatusDemanda.EM_ANDAMENTO,
        )
        self.item = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Impressora", quantidade=1,
            valor_estimado=Decimal("800"), valor_total=Decimal("800"),
            data_prevista=date(2027, 5, 1), prioridade="media",
            justificativa_prioridade="a", justificativa_necessidade="b",
            indicacao_orcamentaria="c", status=StatusItemDemanda.DEVOLVIDA,
        )
        from apps.validacoes.models import Validacao, TipoAcao
        self.val1 = Validacao.objects.create(
            item_demanda=self.item, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario="Primeira devolução: ajustar marca."
        )

    def test_item_devolvido_exibe_ultima_justificativa(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:item-detail", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["justificativa_devolucao"], "Primeira devolução: ajustar marca.")
        self.assertIsNotNone(resp.data["ultima_devolucao"])
        self.assertEqual(resp.data["ultima_devolucao"]["comentario"], "Primeira devolução: ajustar marca.")

    def test_item_devolvido_exibe_justificativa_mais_recente(self):
        from apps.validacoes.models import Validacao, TipoAcao
        Validacao.objects.create(
            item_demanda=self.item, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario="Segunda devolução: ajustar cotação."
        )
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:item-detail", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["justificativa_devolucao"], "Segunda devolução: ajustar cotação.")
        self.assertEqual(Validacao.objects.filter(item_demanda=self.item).count(), 2)

    def test_editar_item_devolvido_salva_observacoes_e_mantem_status(self):
        from apps.validacoes.models import Validacao
        validacoes_antes = Validacao.objects.filter(item_demanda=self.item).count()
        self.client.force_login(self.user)
        resp = self.client.put(
            reverse("api:item-detail", kwargs={"pk": self.item.pk}),
            {
                "tipo": "material", "nome": "Impressora Laser", "descricao": "Multifuncional",
                "unidade_medida": "un", "quantidade": 2, "valor_estimado": "900.00",
                "data_prevista": "2027-05-01", "prioridade": "media",
                "justificativa_prioridade": "a", "justificativa_necessidade": "b",
                "indicacao_orcamentaria": "c", "observacoes": "Ajustada marca e modelo conforme solicitado.",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.nome, "Impressora Laser")
        self.assertEqual(self.item.observacoes, "Ajustada marca e modelo conforme solicitado.")
        self.assertEqual(self.item.status, StatusItemDemanda.DEVOLVIDA)
        # Comprova diretamente que edição NÃO cria nem altera instâncias de Validacao
        self.assertEqual(Validacao.objects.filter(item_demanda=self.item).count(), validacoes_antes)

    def test_observacao_do_solicitante_nao_substitui_justificativa_admin(self):
        from apps.validacoes.models import Validacao
        validacoes_antes = Validacao.objects.filter(item_demanda=self.item).count()
        self.client.force_login(self.user)
        self.client.patch(
            reverse("api:item-detail", kwargs={"pk": self.item.pk}),
            {"observacoes": "Observação do usuário"},
            format="json",
        )
        self.val1.refresh_from_db()
        self.assertEqual(self.val1.comentario, "Primeira devolução: ajustar marca.")
        self.assertEqual(Validacao.objects.filter(item_demanda=self.item).count(), validacoes_antes)

    def test_reenviar_item_devolvido_sucesso(self):
        from apps.validacoes.models import Validacao
        validacoes_antes = Validacao.objects.filter(item_demanda=self.item).count()
        self.client.force_login(self.user)
        resp = self.client.post(reverse("api:item-reenviar", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["detail"], "Item reenviado para validação com sucesso.")
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusItemDemanda.AGUARDANDO_VALIDACAO)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.AGUARDANDO_VALIDACAO)
        # Comprova diretamente que o reenvio NÃO cria nenhuma validação artificial
        self.assertEqual(Validacao.objects.filter(item_demanda=self.item).count(), validacoes_antes)

    def test_demanda_detail_query_count_does_not_grow_per_item(self):
        from apps.validacoes.models import Validacao, TipoAcao
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        d1 = Demanda.objects.create(unidade=self.unidade, usuario=self.user, ano_referencia=2027)
        i1 = ItemDemanda.objects.create(
            demanda=d1, tipo="material", nome="Item 1", quantidade=1,
            valor_estimado=Decimal("100"), valor_total=Decimal("100"),
            data_prevista=date(2027, 1, 1), status=StatusItemDemanda.DEVOLVIDA,
            justificativa_necessidade="N",
        )
        Validacao.objects.create(item_demanda=i1, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario="Dev1")

        d2 = Demanda.objects.create(unidade=self.unidade, usuario=self.user, ano_referencia=2027)
        for idx in range(5):
            it = ItemDemanda.objects.create(
                demanda=d2, tipo="material", nome=f"Item {idx}", quantidade=1,
                valor_estimado=Decimal("100"), valor_total=Decimal("100"),
                data_prevista=date(2027, 1, 1), status=StatusItemDemanda.DEVOLVIDA,
                justificativa_necessidade="N",
            )
            Validacao.objects.create(item_demanda=it, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario=f"Dev {idx}")

        self.client.force_login(self.user)

        with CaptureQueriesContext(connection) as ctx1:
            self.client.get(reverse("api:demanda-detail", kwargs={"pk": d1.pk}))

        with CaptureQueriesContext(connection) as ctx2:
            self.client.get(reverse("api:demanda-detail", kwargs={"pk": d2.pk}))

        self.assertEqual(len(ctx1), len(ctx2))

    def test_reenviar_item_nao_devolvido_rejeita(self):
        self.item.status = StatusItemDemanda.AGUARDANDO_VALIDACAO
        self.item.save()
        self.client.force_login(self.user)
        resp = self.client.post(reverse("api:item-reenviar", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reenviar_item_de_demanda_concluida_rejeita(self):
        self.demanda.status = StatusDemanda.CONCLUIDA
        self.demanda.save()
        self.client.force_login(self.user)
        resp = self.client.post(reverse("api:item-reenviar", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_outro_usuario_nao_edita_nem_reenvia_item(self):
        self.client.force_login(self.outro_user)
        edit_resp = self.client.patch(
            reverse("api:item-detail", kwargs={"pk": self.item.pk}),
            {"nome": "Hacked"}, format="json",
        )
        self.assertEqual(edit_resp.status_code, status.HTTP_404_NOT_FOUND)

        resend_resp = self.client.post(reverse("api:item-reenviar", kwargs={"pk": self.item.pk}))
        self.assertEqual(resend_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_visualiza_mas_nao_edita_item(self):
        self.client.force_login(self.admin)
        get_resp = self.client.get(reverse("api:item-detail", kwargs={"pk": self.item.pk}))
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)

        edit_resp = self.client.patch(
            reverse("api:item-detail", kwargs={"pk": self.item.pk}),
            {"nome": "Admin Edit"}, format="json",
        )
        self.assertEqual(edit_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_segundo_reenvio_do_mesmo_item_eh_rejeitado(self):
        from apps.validacoes.models import Validacao
        self.client.force_login(self.user)
        # Primeiro reenvio: sucesso
        resp1 = self.client.post(reverse("api:item-reenviar", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusItemDemanda.AGUARDANDO_VALIDACAO)

        val_count_before = Validacao.objects.filter(item_demanda=self.item).count()

        # Segundo reenvio: rejeitado por transição inválida
        resp2 = self.client.post(reverse("api:item-reenviar", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, StatusItemDemanda.AGUARDANDO_VALIDACAO)
        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.status, StatusDemanda.AGUARDANDO_VALIDACAO)
        self.assertEqual(Validacao.objects.filter(item_demanda=self.item).count(), val_count_before)

    def test_get_item_proprietario_acessa(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:item-detail", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.item.pk)
        self.assertEqual(resp.data["demanda"], self.demanda.pk)

    def test_get_item_outro_usuario_bloqueado(self):
        self.client.force_login(self.outro_user)
        resp = self.client.get(reverse("api:item-detail", kwargs={"pk": self.item.pk}))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_inexistente_retorna_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:item-detail", kwargs={"pk": 999999}))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_prefetch_multiplos_itens_devolvidos(self):
        from apps.validacoes.models import Validacao, TipoAcao
        item2 = ItemDemanda.objects.create(
            demanda=self.demanda, tipo="material", nome="Monitor 27", quantidade=2,
            valor_estimado=Decimal("1200"), valor_total=Decimal("2400"),
            data_prevista=date(2027, 5, 1), prioridade="alta",
            justificativa_prioridade="a", justificativa_necessidade="b",
            indicacao_orcamentaria="c", status=StatusItemDemanda.DEVOLVIDA,
        )
        Validacao.objects.create(
            item_demanda=item2, usuario=self.admin, acao=TipoAcao.DEVOLVIDO, comentario="Devolução Monitor: ajustar resolução."
        )

        self.client.force_login(self.user)
        resp = self.client.get(reverse("api:demanda-detail", kwargs={"pk": self.demanda.pk}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        itens = resp.data["itens"]
        self.assertEqual(len(itens), 2)
        i1 = next(i for i in itens if i["id"] == self.item.pk)
        i2 = next(i for i in itens if i["id"] == item2.pk)
        self.assertEqual(i1["justificativa_devolucao"], "Primeira devolução: ajustar marca.")
        self.assertEqual(i2["justificativa_devolucao"], "Devolução Monitor: ajustar resolução.")


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
