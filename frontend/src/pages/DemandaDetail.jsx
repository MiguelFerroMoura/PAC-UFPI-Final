import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import Spinner from "../components/Spinner";
import { formatCurrency, statusBadge, statusLabel } from "../utils/format";

export default function DemandaDetail() {
  const { id } = useParams();
  const [demanda, setDemanda] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");

  const carregar = useCallback(() => {
    setCarregando(true);
    return api
      .getDemanda(id)
      .then(setDemanda)
      .catch((e) => setErro(e.message))
      .finally(() => setCarregando(false));
  }, [id]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function handleEnviar() {
    setErro("");
    setMensagem("");
    try {
      const atualizada = await api.enviarDemanda(id);
      setDemanda(atualizada);
      setMensagem("Demanda enviada para validação.");
    } catch (e) {
      setErro(e.message);
    }
  }

  if (carregando) return <Spinner />;
  if (erro && !demanda)
    return (
      <div className="alert alert-danger" role="alert">
        {erro}
      </div>
    );
  if (!demanda) return null;

  const isRascunho = demanda.status === "rascunho";

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1 className="h3 mb-0">Demanda #{demanda.id}</h1>
        <span className={`badge fs-6 ${statusBadge(demanda.status)}`}>
          {statusLabel(demanda.status)}
        </span>
      </div>

      {mensagem && (
        <div className="alert alert-success" role="alert">
          {mensagem}
        </div>
      )}
      {erro && (
        <div className="alert alert-danger" role="alert">
          {erro}
        </div>
      )}

      <dl className="row">
        <dt className="col-sm-3">Unidade</dt>
        <dd className="col-sm-9">{demanda.unidade_sigla}</dd>
        <dt className="col-sm-3">Ano de referência</dt>
        <dd className="col-sm-9">{demanda.ano_referencia}</dd>
        <dt className="col-sm-3">Responsável</dt>
        <dd className="col-sm-9">{demanda.usuario_nome}</dd>
      </dl>

      <div className="d-flex justify-content-between align-items-center mb-2">
        <h2 className="h5 mb-0">Itens</h2>
        {isRascunho && (
          <Link
            to={`/demandas/${demanda.id}/itens/novo`}
            className="btn btn-sm btn-outline-primary"
          >
            <i className="bi bi-plus-lg me-1"></i>Adicionar item
          </Link>
        )}
      </div>

      {demanda.itens.length === 0 ? (
        <p className="text-muted">Nenhum item adicionado.</p>
      ) : (
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Qtd.</th>
                <th>Valor unit.</th>
                <th>Valor total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {demanda.itens.map((item) => (
                <tr key={item.id}>
                  <td>{item.nome}</td>
                  <td>{item.quantidade}</td>
                  <td>{formatCurrency(item.valor_estimado)}</td>
                  <td>{formatCurrency(item.valor_total)}</td>
                  <td>
                    <span className={`badge ${statusBadge(item.status)}`}>
                      {statusLabel(item.status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th colSpan={3} className="text-end">
                  Total
                </th>
                <th>{formatCurrency(demanda.valor_total)}</th>
                <th></th>
              </tr>
            </tfoot>
          </table>
        </div>
      )}

      {isRascunho && demanda.itens.length > 0 && (
        <button className="btn btn-success mt-3" onClick={handleEnviar}>
          <i className="bi bi-send me-1"></i>Enviar para validação
        </button>
      )}
    </div>
  );
}
