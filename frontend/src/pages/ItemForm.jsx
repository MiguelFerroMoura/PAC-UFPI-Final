import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";

const CAMPOS_INICIAIS = {
  tipo: "material",
  nome: "",
  descricao: "",
  unidade_medida: "",
  quantidade: 1,
  valor_estimado: "",
  data_prevista: "",
  prioridade: "media",
  justificativa_prioridade: "",
  justificativa_necessidade: "",
  indicacao_orcamentaria: "",
};

export default function ItemForm() {
  const { id } = useParams(); // id da demanda
  const navigate = useNavigate();
  const [form, setForm] = useState(CAMPOS_INICIAIS);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  function atualizar(campo, valor) {
    setForm((atual) => ({ ...atual, [campo]: valor }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await api.addItem(id, {
        ...form,
        quantidade: Number(form.quantidade),
      });
      navigate(`/demandas/${id}`);
    } catch (err) {
      setErro(err.message || "Não foi possível adicionar o item.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <h1 className="h4 mb-3">Adicionar item</h1>

        {erro && (
          <div className="alert alert-danger" role="alert">
            {erro}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="row g-3">
            <div className="col-md-4">
              <label htmlFor="tipo" className="form-label">
                Tipo
              </label>
              <select
                id="tipo"
                className="form-select"
                value={form.tipo}
                onChange={(e) => atualizar("tipo", e.target.value)}
              >
                <option value="material">Material</option>
                <option value="servico">Serviço</option>
              </select>
            </div>
            <div className="col-md-8">
              <label htmlFor="nome" className="form-label">
                Nome
              </label>
              <input
                id="nome"
                className="form-control"
                value={form.nome}
                onChange={(e) => atualizar("nome", e.target.value)}
                required
              />
            </div>
            <div className="col-12">
              <label htmlFor="descricao" className="form-label">
                Descrição
              </label>
              <textarea
                id="descricao"
                className="form-control"
                rows={2}
                value={form.descricao}
                onChange={(e) => atualizar("descricao", e.target.value)}
                required
              />
            </div>
            <div className="col-md-4">
              <label htmlFor="unidade_medida" className="form-label">
                Unidade de medida
              </label>
              <input
                id="unidade_medida"
                className="form-control"
                value={form.unidade_medida}
                onChange={(e) => atualizar("unidade_medida", e.target.value)}
                required
              />
            </div>
            <div className="col-md-4">
              <label htmlFor="quantidade" className="form-label">
                Quantidade
              </label>
              <input
                id="quantidade"
                type="number"
                min="1"
                className="form-control"
                value={form.quantidade}
                onChange={(e) => atualizar("quantidade", e.target.value)}
                required
              />
            </div>
            <div className="col-md-4">
              <label htmlFor="valor_estimado" className="form-label">
                Valor estimado unitário
              </label>
              <input
                id="valor_estimado"
                type="number"
                step="0.01"
                className="form-control"
                value={form.valor_estimado}
                onChange={(e) => atualizar("valor_estimado", e.target.value)}
                required
              />
            </div>
            <div className="col-md-4">
              <label htmlFor="data_prevista" className="form-label">
                Data prevista
              </label>
              <input
                id="data_prevista"
                type="date"
                className="form-control"
                value={form.data_prevista}
                onChange={(e) => atualizar("data_prevista", e.target.value)}
                required
              />
            </div>
            <div className="col-md-4">
              <label htmlFor="prioridade" className="form-label">
                Prioridade
              </label>
              <select
                id="prioridade"
                className="form-select"
                value={form.prioridade}
                onChange={(e) => atualizar("prioridade", e.target.value)}
              >
                <option value="baixa">Baixa</option>
                <option value="media">Média</option>
                <option value="alta">Alta</option>
                <option value="critica">Crítica</option>
              </select>
            </div>
            <div className="col-md-4">
              <label htmlFor="indicacao_orcamentaria" className="form-label">
                Indicação orçamentária
              </label>
              <input
                id="indicacao_orcamentaria"
                className="form-control"
                value={form.indicacao_orcamentaria}
                onChange={(e) =>
                  atualizar("indicacao_orcamentaria", e.target.value)
                }
                required
              />
            </div>
            <div className="col-md-6">
              <label htmlFor="justificativa_prioridade" className="form-label">
                Justificativa da prioridade
              </label>
              <textarea
                id="justificativa_prioridade"
                className="form-control"
                rows={2}
                value={form.justificativa_prioridade}
                onChange={(e) =>
                  atualizar("justificativa_prioridade", e.target.value)
                }
                required
              />
            </div>
            <div className="col-md-6">
              <label htmlFor="justificativa_necessidade" className="form-label">
                Justificativa da necessidade
              </label>
              <textarea
                id="justificativa_necessidade"
                className="form-control"
                rows={2}
                value={form.justificativa_necessidade}
                onChange={(e) =>
                  atualizar("justificativa_necessidade", e.target.value)
                }
                required
              />
            </div>
          </div>

          <button className="btn btn-primary mt-3" disabled={enviando}>
            {enviando ? "Salvando..." : "Adicionar item"}
          </button>
        </form>
      </div>
    </div>
  );
}
