import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import Spinner from "../components/Spinner";
import { formatCurrency, statusLabel } from "../utils/format";

export default function DemandaDetail() {
  const { id } = useParams();
  const [demanda, setDemanda] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [enviando, setEnviando] = useState(false);

  const carregar = useCallback(() => {
    setCarregando(true); setErro("");
    return api.getDemanda(id).then(setDemanda).catch((e) => setErro(e.message)).finally(() => setCarregando(false));
  }, [id]);

  useEffect(() => { carregar(); }, [carregar]);

  async function handleEnviar() {
    if (!window.confirm("Enviar esta demanda para validação? Depois do envio, ela não poderá ser editada como rascunho.")) return;
    setErro(""); setMensagem(""); setEnviando(true);
    try { setDemanda(await api.enviarDemanda(id)); setMensagem("Demanda enviada para validação."); }
    catch (e) { setErro(e.message); }
    finally { setEnviando(false); }
  }

  if (carregando) return <Spinner />;
  if (erro && !demanda) return <div className="alert alert-danger"><i className="bi bi-exclamation-triangle me-2" />{erro}</div>;
  if (!demanda) return null;

  const isRascunho = demanda.status === "rascunho";
  const itens = demanda.itens || [];

  return (
    <div>
      <div className="page-head">
        <div>
          <Link to="/demandas" className="text-decoration-none small text-primary"><i className="bi bi-arrow-left me-1" />Voltar para demandas</Link>
          <div className="d-flex align-items-center gap-2 mt-2"><span className="page-kicker">Demanda #{demanda.id}</span><span className={`badge-status ${demanda.status}`}>{statusLabel(demanda.status)}</span></div>
          <h1>{demanda.unidade_sigla} · {demanda.ano_referencia}</h1><p>Responsável: {demanda.usuario_nome}</p>
        </div>
        {isRascunho && <Link to={`/demandas/${id}/editar`} className="btn btn-outline-primary"><i className="bi bi-pencil me-2" />Editar</Link>}
      </div>

      {mensagem && <div className="alert alert-success"><i className="bi bi-check-circle me-2" />{mensagem}</div>}
      {erro && <div className="alert alert-danger"><i className="bi bi-exclamation-triangle me-2" />{erro}</div>}

      <div className="detail-layout">
        <section className="info-panel">
          <div className="card-header-clean"><div><span className="card-kicker">Itens da demanda</span><h2 className="card-title-sm">{itens.length} item(ns) cadastrado(s)</h2></div>{isRascunho && <Link to={`/demandas/${id}/itens/novo`} className="btn btn-sm btn-primary"><i className="bi bi-plus-lg me-1" />Adicionar item</Link>}</div>
          {itens.length === 0 ? <div className="empty"><div className="empty-icon"><i className="bi bi-basket" /></div><h3>Demanda sem itens</h3><p>Adicione pelo menos um item antes de enviar para validação.</p></div> : (
            <div className="table-responsive">
              <table className="table"><thead><tr><th>Item</th><th>Qtd.</th><th>Unitário</th><th>Total</th><th>Status</th></tr></thead>
              <tbody>{itens.map((item) => <tr key={item.id}><td><strong>{item.nome}</strong><small className="d-block muted-label">{item.tipo || "Item de contratação"}</small></td><td>{item.quantidade}</td><td>{formatCurrency(item.valor_estimado)}</td><td className="fw-semibold">{formatCurrency(item.valor_total)}</td><td><span className={`badge-status ${item.status}`}>{statusLabel(item.status)}</span></td></tr>)}</tbody>
              <tfoot><tr><th colSpan={3} className="text-end">Total da demanda</th><th>{formatCurrency(demanda.valor_total)}</th><th /></tr></tfoot>
              </table>
            </div>
          )}
        </section>

        <aside className="summary-panel">
          <span className="label">Resumo financeiro</span><div className="total">{formatCurrency(demanda.valor_total)}</div><hr />
          <div className="summary-row"><span>Ano de referência</span><strong>{demanda.ano_referencia}</strong></div>
          <div className="summary-row"><span>Itens</span><strong>{itens.length}</strong></div>
          <div className="summary-row"><span>Status</span><strong>{statusLabel(demanda.status)}</strong></div>
          {isRascunho && itens.length > 0 && <button className="btn btn-light w-100 mt-4" onClick={handleEnviar} disabled={enviando}>{enviando ? "Enviando..." : <><i className="bi bi-send me-2" />Enviar para validação</>}</button>}
        </aside>
      </div>
    </div>
  );
}
