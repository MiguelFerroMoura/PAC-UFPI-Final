import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../auth/AuthContext";

function initials(user) {
  const name = user?.nome_completo || user?.username || "U";
  return name.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

export default function Layout() {
  const { user, isStaff, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  async function handleLogout() {
    await logout();
    setMenuOpen(false);
    navigate("/login");
  }

  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="app-shell">
      {menuOpen && <button className="sidebar-overlay" aria-label="Fechar menu" onClick={closeMenu} />}
      <aside className={`app-sidebar ${menuOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><i className="bi bi-clipboard2-check" /></div>
          <div>
            <span className="brand-title">PAC UFPI</span>
            <span className="brand-subtitle">Plano Anual de Contratações</span>
          </div>
        </div>

        <div className="sidebar-section">Navegação</div>
        <nav className="sidebar-nav">
          <NavLink to="/" end className="nav-link" onClick={closeMenu}>
            <i className="bi bi-grid-1x2" /> Início
          </NavLink>
          {user && (
            <>
              <NavLink to="/demandas" className="nav-link" onClick={closeMenu}>
                <i className="bi bi-file-earmark-text" /> Demandas
              </NavLink>
              <NavLink to="/catalogo" className="nav-link" onClick={closeMenu}>
                <i className="bi bi-box-seam" /> Catálogo
              </NavLink>
              <NavLink to="/dashboard" className="nav-link" onClick={closeMenu}>
                <i className="bi bi-bar-chart-line" /> Dashboard
              </NavLink>
            </>
          )}
        </nav>

        {isStaff && (
          <>
            <div className="sidebar-section">Gestão</div>
            <nav className="sidebar-nav">
              <NavLink to="/validacoes" className="nav-link" onClick={closeMenu}>
                <i className="bi bi-check2-square" /> Validações
              </NavLink>
              <NavLink to="/dfds" className="nav-link" onClick={closeMenu}>
                <i className="bi bi-file-earmark-ruled" /> DFDs
              </NavLink>
            </nav>
          </>
        )}

        <div className="sidebar-bottom">
          <span className="online-dot" /> Sistema conectado
        </div>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <div className="d-flex align-items-center gap-3">
            <button className="mobile-toggle" onClick={() => setMenuOpen(true)} aria-label="Abrir menu">
              <i className="bi bi-list" />
            </button>
            <div>
              <span className="topbar-label">Sistema de Gestão do PAC</span>
              <span className="topbar-context">Universidade Federal do Piauí</span>
            </div>
          </div>

          {user ? (
            <div className="dropdown">
              <button className="user-chip" data-bs-toggle="dropdown" aria-expanded="false">
                <span className="user-avatar">{initials(user)}</span>
                <span className="user-meta d-none d-sm-block">
                  <strong>{user.nome_completo || user.username}</strong>
                  <small>{isStaff ? "Administrador" : "Usuário"}</small>
                </span>
                <i className="bi bi-chevron-down text-muted small" />
              </button>
              <ul className="dropdown-menu dropdown-menu-end shadow-sm border-0">
                <li><span className="dropdown-item-text small text-muted">{user.username}</span></li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <button className="dropdown-item text-danger" onClick={handleLogout}>
                    <i className="bi bi-box-arrow-right me-2" />Sair
                  </button>
                </li>
              </ul>
            </div>
          ) : (
            <Link className="btn btn-primary btn-sm px-3" to="/login">Entrar</Link>
          )}
        </header>

        <main className="app-content"><Outlet /></main>
        <footer className="app-footer">PAC UFPI · Sistema de Gestão do Plano Anual de Contratações</footer>
      </div>
    </div>
  );
}
