import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithRouter } from "../test-utils";
import ItemForm from "./ItemForm";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: { addItem: vi.fn(), getItem: vi.fn(), updateItem: vi.fn() },
}));

async function preencherObrigatorios() {
  await userEvent.type(screen.getByLabelText(/^nome$/i), "Notebook");
  await userEvent.type(screen.getByLabelText(/descrição/i), "Notebook i5");
  await userEvent.type(screen.getByLabelText(/unidade de medida/i), "unidade");
  await userEvent.clear(screen.getByLabelText(/quantidade/i));
  await userEvent.type(screen.getByLabelText(/quantidade/i), "2");
  await userEvent.type(screen.getByLabelText(/valor estimado/i), "1500");
  await userEvent.type(screen.getByLabelText(/data prevista/i), "2027-01-01");
  await userEvent.type(screen.getByLabelText(/indicação orçamentária/i), "Orc 1");
  await userEvent.type(screen.getByLabelText(/justificativa da prioridade/i), "Alta");
  await userEvent.type(screen.getByLabelText(/justificativa da necessidade/i), "Uso");
}

describe("ItemForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("adiciona item à demanda e navega de volta ao detalhe", async () => {
    api.addItem.mockResolvedValue({ id: 10 });
    renderWithRouter(<ItemForm />, {
      route: "/demandas/7/itens/novo",
      path: "/demandas/:id/itens/novo",
      extraRoutes: [{ path: "/demandas/:id", element: <p>detalhe demanda</p> }],
    });

    await preencherObrigatorios();
    await userEvent.click(
      screen.getByRole("button", { name: /adicionar item/i })
    );

    await waitFor(() => expect(api.addItem).toHaveBeenCalledTimes(1));
    const [demandaId, payload] = api.addItem.mock.calls[0];
    expect(demandaId).toBe("7");
    expect(payload).toMatchObject({ nome: "Notebook", quantidade: 2 });
    expect(await screen.findByText("detalhe demanda")).toBeInTheDocument();
  });

  it("mostra erro quando a API rejeita adição", async () => {
    api.addItem.mockRejectedValue(new Error("Demanda não está em rascunho"));
    renderWithRouter(<ItemForm />, {
      route: "/demandas/7/itens/novo",
      path: "/demandas/:id/itens/novo",
    });
    await preencherObrigatorios();
    await userEvent.click(
      screen.getByRole("button", { name: /adicionar item/i })
    );
    expect(
      await screen.findByText(/não está em rascunho/i)
    ).toBeInTheDocument();
  });

  it("modo de edição carrega item por URL direta e preenche campos com observacoes", async () => {
    api.getItem.mockResolvedValue({
      id: 10,
      demanda: 7,
      tipo: "material",
      nome: "Impressora Laser",
      descricao: "LaserJet Pro",
      unidade_medida: "un",
      quantidade: 3,
      valor_estimado: "1200.00",
      data_prevista: "2027-06-01",
      prioridade: "alta",
      indicacao_orcamentaria: "Orc 2027",
      justificativa_prioridade: "Prioridade alta",
      justificativa_necessidade: "Impressões urgentes",
      observacoes: "Marca especificada",
      status: "devolvida",
    });
    api.updateItem.mockResolvedValue({ id: 10 });

    renderWithRouter(<ItemForm />, {
      route: "/demandas/7/itens/10/editar",
      path: "/demandas/:id/itens/:itemId/editar",
      extraRoutes: [{ path: "/demandas/:id", element: <p>detalhe demanda</p> }],
    });

    expect(await screen.findByText("Editar item")).toBeInTheDocument();
    expect(api.getItem).toHaveBeenCalledWith("10");
    expect(screen.getByLabelText(/^nome$/i)).toHaveValue("Impressora Laser");
    expect(screen.getByLabelText(/observações do solicitante/i)).toHaveValue("Marca especificada");

    await userEvent.clear(screen.getByLabelText(/observações do solicitante/i));
    await userEvent.type(screen.getByLabelText(/observações do solicitante/i), "Observação atualizada");

    await userEvent.click(screen.getByRole("button", { name: /salvar alterações/i }));

    await waitFor(() => expect(api.updateItem).toHaveBeenCalledTimes(1));
    const [itemId, payload] = api.updateItem.mock.calls[0];
    expect(itemId).toBe("10");
    expect(payload).toMatchObject({
      nome: "Impressora Laser",
      quantidade: 3,
      observacoes: "Observação atualizada",
    });
    expect(payload).not.toHaveProperty("status");
    expect(await screen.findByText("detalhe demanda")).toBeInTheDocument();
  });

  it("valida que o item pertence à demanda da rota", async () => {
    api.getItem.mockResolvedValue({
      id: 10,
      demanda: 99, // Demanda diferente de 7
      nome: "Item Outra Demanda",
    });

    renderWithRouter(<ItemForm />, {
      route: "/demandas/7/itens/10/editar",
      path: "/demandas/:id/itens/:itemId/editar",
    });

    expect(
      await screen.findByText(/este item não pertence à demanda informada/i)
    ).toBeInTheDocument();
  });
});

