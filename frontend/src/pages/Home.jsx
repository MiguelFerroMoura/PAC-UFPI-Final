import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Home() {
  const { user, isStaff } = useAuth();
  const nome = user?.nome_completo || user?.username || "";

  return (
    <div>
      <section className="hero">
        <span className="page-kicker">Planejamento institucional</span>
        <h1>{user ? `Olá, ${nome.split(" ")[0]}` : "PAC UFPI"}</h1>
        <p>
          {user
            ? "Organize suas demandas de contratação, acompanhe validações e consulte a consolidação do Plano Anual de Contratações."
            : "Sistema de Gestão do Plano Anual de Contratações da Universidade Federal do Piauí."}
        </p>
        <div className="hero-actions">
          {user ? (
            <>
              <Link to="/demandas/nova" className="btn btn-light">
                <i className="bi bi-plus-lg me-2" />Nova demanda
              </Link>
              <Link to="/dashboard" className="btn btn-outline-light">
                <i className="bi bi-bar-chart-line me-2" />Ver indicadores
              </Link>
            </>
          ) : (
            <Link to="/login" className="btn btn-light">Entrar no sistema <i className="bi bi-arrow-right ms-2" /></Link>
          )}
        </div>
      </section>

      {user ? (
        <>
          <div className="d-flex justify-content-between align-items-end mb-3">
            <div>
              <span className="page-kicker">Acesso rápido</span>
              <h2 className="h5 fw-bold mb-0 mt-1">Módulos do sistema</h2>
            </div>
          </div>
          <div className="quick-grid">
            <Link to="/demandas" className="quick-card">
              <span className="quick-icon"><i className="bi bi-file-earmark-text" /></span>
              <span><h3>Demandas</h3><p>Cadastre e acompanhe solicitações de contratação.</p></span>
              <i className="bi bi-arrow-right quick-arrow" />
            </Link>
            <Link to="/catalogo" className="quick-card">
              <span className="quick-icon"><i className="bi bi-box-seam" /></span>
              <span><h3>Catálogo</h3><p>Consulte materiais e serviços disponíveis.</p></span>
              <i className="bi bi-arrow-right quick-arrow" />
            </Link>
            <Link to="/dashboard" className="quick-card">
              <span className="quick-icon"><i className="bi bi-bar-chart-line" /></span>
              <span><h3>Dashboard</h3><p>Visualize os principais indicadores do PAC.</p></span>
              <i className="bi bi-arrow-right quick-arrow" />
            </Link>
            {isStaff && (
              <>
                <Link to="/validacoes" className="quick-card">
                  <span className="quick-icon"><i className="bi bi-check2-square" /></span>
                  <span><h3>Validações</h3><p>Analise itens enviados pelas unidades.</p></span>
                  <i className="bi bi-arrow-right quick-arrow" />
                </Link>
                <Link to="/dfds" className="quick-card">
                  <span className="quick-icon"><i className="bi bi-file-earmark-ruled" /></span>
                  <span><h3>DFDs</h3><p>Consolide itens validados em documentos.</p></span>
                  <i className="bi bi-arrow-right quick-arrow" />
                </Link>
              </>
            )}
          </div>
        </>
      ) : (
        <div className="row g-3">
          {["Planejamento centralizado","Fluxo de validação","Consolidação em DFD"].map((item, index) => (
            <div className="col-md-4" key={item}>
              <div className="pac-card h-100 p-4">
                <div className="quick-icon mb-3"><i className={`bi ${["bi-diagram-3","bi-check2-circle","bi-file-earmark-ruled"][index]}`} /></div>
                <h3 className="h6 fw-bold">{item}</h3>
                <p className="text-muted small mb-0">Um fluxo único para organizar o planejamento anual de contratações.</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
