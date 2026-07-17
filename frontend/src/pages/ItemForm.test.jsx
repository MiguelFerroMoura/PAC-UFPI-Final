import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithRouter } from "../test-utils";
import ItemForm from "./ItemForm";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: { addItem: vi.fn() },
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

  it("mostra erro quando a API rejeita", async () => {
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
});
