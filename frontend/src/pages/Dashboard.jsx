import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import Spinner from "../components/Spinner";
import { formatCurrency, statusLabel, statusBadge } from "../utils/format";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    api.dashboardStats().then(setStats).catch((e) => setErro(e.message)).finally(() => setCarregando(false));
  }, []);

  if (carregando) return <Spinner />;
  if (erro) return <div className="alert alert-danger"><i className="bi bi-exclamation-triangle me-2" />{erro}</div>;

  const cards = [
    ["Demandas", stats.total_demandas, "bi-file-earmark-text", ""],
    ["Itens", stats.total_itens, "bi-list-check", ""],
    ["Aguardando validação", stats.aguardando_validacao, "bi-hourglass-split", "warning"],
    ["Validados", stats.validados, "bi-check2-circle", "success"],
  ];

  return (
    <div>
      <div className="page-head">
        <div><span className="page-kicker">Visão geral</span><h1>Dashboard</h1><p>Acompanhe o andamento do planejamento de contratações.</p></div>
        <Link to="/demandas/nova" className="btn btn-primary"><i className="bi bi-plus-lg me-2" />Nova demanda</Link>
      </div>

      <div className="stats-grid">
        {cards.map(([label, value, icon, tone]) => (
          <div className="stat" key={label}>
            <div className={`stat-icon ${tone}`}><i className={`bi ${icon}`} /></div>
            <div><span className="stat-label">{label}</span><strong className="stat-value">{value}</strong></div>
          </div>
        ))}
      </div>

      <div className="row g-3">
        <div className="col-lg-7">
          <div className="pac-card h-100">
            <div className="card-header-clean"><div><span className="card-kicker">Distribuição</span><h2 className="card-title-sm">Itens por status</h2></div><i className="bi bi-pie-chart text-muted" /></div>
            <div className="p-3">
              {Object.entries(stats.itens_por_status || {}).length === 0 ? (
                <div className="empty py-4"><div className="empty-icon"><i className="bi bi-inbox" /></div><p>Nenhum dado disponível.</p></div>
              ) : Object.entries(stats.itens_por_status).map(([status, total]) => (
                <div className="d-flex align-items-center justify-content-between py-2 border-bottom" key={status}>
                  <span className={`badge-status ${statusBadge(status).replace("bg-","")}`}>{statusLabel(status)}</span>
                  <strong>{total}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="col-lg-5">
          <div className="summary-panel h-100">
            <span className="label">Valor total estimado</span>
            <div className="total">{formatCurrency(stats.valor_total_estimado)}</div>
            <hr />
            <div className="summary-row"><span>Demandas cadastradas</span><strong>{stats.total_demandas}</strong></div>
            <div className="summary-row"><span>Itens consolidados</span><strong>{stats.consolidados}</strong></div>
            <div className="summary-row"><span>DFDs gerados</span><strong>{stats.total_dfds}</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
}
