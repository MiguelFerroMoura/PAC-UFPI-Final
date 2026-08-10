import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithRouter } from "../test-utils";
import DemandaDetail from "./DemandaDetail";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: { getDemanda: vi.fn(), enviarDemanda: vi.fn() },
}));

const demandaRascunho = {
  id: 7,
  unidade_sigla: "STI",
  ano_referencia: 2027,
  usuario_nome: "Ana Silva",
  status: "rascunho",
  valor_total: 3000,
  itens: [
    {
      id: 1,
      nome: "Notebook",
      quantidade: 2,
      valor_estimado: 1500,
      valor_total: 3000,
      status: "rascunho",
    },
  ],
};

function renderDetail() {
  return renderWithRouter(<DemandaDetail />, {
    route: "/demandas/7",
    path: "/demandas/:id",
  });
}

describe("DemandaDetail", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("exibe os dados e itens da demanda", async () => {
    api.getDemanda.mockResolvedValue(demandaRascunho);
    renderDetail();
    expect(await screen.findByText("Demanda #7")).toBeInTheDocument();
    expect(screen.getByText("Notebook")).toBeInTheDocument();
    expect(screen.getByText("Ana Silva")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /enviar para validação/i })).toBeInTheDocument();
  });

  it("envia a demanda para validação", async () => {
    api.getDemanda.mockResolvedValue(demandaRascunho);
    api.enviarDemanda.mockResolvedValue({
      ...demandaRascunho,
      status: "aguardando_validacao",
    });
    renderDetail();
    await screen.findByText("Demanda #7");
    await userEvent.click(
      screen.getByRole("button", { name: /enviar para validação/i })
    );
    await waitFor(() =>
      expect(api.enviarDemanda).toHaveBeenCalledWith("7")
    );
    expect(
      await screen.findByText(/enviada para validação/i)
    ).toBeInTheDocument();
  });

  it("não mostra botão de enviar quando não está em rascunho", async () => {
    api.getDemanda.mockResolvedValue({
      ...demandaRascunho,
      status: "validada",
    });
    renderDetail();
    await screen.findByText("Demanda #7");
    expect(
      screen.queryByRole("button", { name: /enviar para validação/i })
    ).not.toBeInTheDocument();
  });
});
