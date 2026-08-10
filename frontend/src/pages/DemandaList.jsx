import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import Spinner from "../components/Spinner";
import { formatCurrency, statusLabel } from "../utils/format";

export default function DemandaList() {
  const [demandas, setDemandas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [busca, setBusca] = useState("");

  useEffect(() => {
    api.listDemandas()
      .then((data) => setDemandas(data.results || data))
      .catch((e) => setErro(e.message))
      .finally(() => setCarregando(false));
  }, []);

  const filtradas = useMemo(() => {
    const q = busca.trim().toLowerCase();
    if (!q) return demandas;
    return demandas.filter((d) =>
      [d.id, d.unidade_sigla, d.ano_referencia, statusLabel(d.status)].join(" ").toLowerCase().includes(q)
    );
  }, [busca, demandas]);

  if (carregando) return <Spinner />;

  return (
    <div>
      <div className="page-head">
        <div><span className="page-kicker">Planejamento</span><h1>Demandas</h1><p>Cadastre e acompanhe as solicitações da sua unidade.</p></div>
        <Link to="/demandas/nova" className="btn btn-primary"><i className="bi bi-plus-lg me-2" />Nova demanda</Link>
      </div>

      {erro && <div className="alert alert-danger"><i className="bi bi-exclamation-triangle me-2" />{erro}</div>}

      <div className="table-shell">
        <div className="table-toolbar">
          <div className="search-control"><i className="bi bi-search" /><input aria-label="Pesquisar demandas" value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Pesquisar por unidade, ano ou status..." /></div>
          <span className="muted-label">{filtradas.length} de {demandas.length} demanda(s)</span>
        </div>
        {filtradas.length === 0 ? (
          <div className="empty">
            <div className="empty-icon"><i className="bi bi-inbox" /></div>
            <h3>{busca ? "Nenhum resultado encontrado" : "Nenhuma demanda cadastrada"}</h3>
            <p>{busca ? "Tente outro termo de pesquisa." : "Comece criando sua primeira demanda."}</p>
            {!busca && <Link to="/demandas/nova" className="btn btn-primary btn-sm">Criar demanda</Link>}
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table align-middle">
              <thead><tr><th>#</th><th>Unidade</th><th>Ano</th><th>Status</th><th>Valor total</th><th /></tr></thead>
              <tbody>
                {filtradas.map((d) => (
                  <tr key={d.id}>
                    <td className="fw-bold">#{d.id}</td><td>{d.unidade_sigla}</td><td>{d.ano_referencia}</td>
                    <td><span className={`badge-status ${d.status}`}>{statusLabel(d.status)}</span></td>
                    <td className="fw-semibold">{formatCurrency(d.valor_total)}</td>
                    <td className="text-end"><Link to={`/demandas/${d.id}`} className="btn btn-sm btn-outline-primary">Abrir <i className="bi bi-arrow-right ms-1" /></Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
