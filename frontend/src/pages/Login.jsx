import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [mostrarSenha, setMostrarSenha] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault(); setErro(""); setEnviando(true);
    try { await login(username.trim(), password); navigate("/"); }
    catch (err) { setErro(err.message || "Não foi possível entrar."); }
    finally { setEnviando(false); }
  }

  return (
    <div className="login-page">
      <section className="login-brand-panel">
        <span className="page-kicker" style={{color:"#b9dcfb"}}>Universidade Federal do Piauí</span>
        <div className="brand-mark mt-4"><i className="bi bi-clipboard2-check" /></div>
        <h1>PAC UFPI</h1>
        <p>Planeje, acompanhe e consolide as contratações institucionais em um único ambiente.</p>
        <div className="login-points">
          <span className="login-point"><i className="bi bi-check-circle-fill" /> Gestão de demandas de contratação</span>
          <span className="login-point"><i className="bi bi-check-circle-fill" /> Fluxo de validação por etapas</span>
          <span className="login-point"><i className="bi bi-check-circle-fill" /> Consolidação em DFDs</span>
        </div>
      </section>
      <section className="login-form-panel">
        <div className="login-box">
          <div className="brand-mark"><i className="bi bi-person-lock" /></div>
          <h2>Bem-vindo de volta</h2>
          <p>Entre com suas credenciais institucionais para continuar.</p>
          {erro && <div className="alert alert-danger small"><i className="bi bi-exclamation-triangle me-2" />{erro}</div>}
          <form onSubmit={handleSubmit}>
            <div className="mb-3"><label htmlFor="username" className="form-label">Usuário</label><input id="username" autoComplete="username" className="form-control form-control-lg" value={username} onChange={(e)=>setUsername(e.target.value)} required /></div>
            <div className="mb-4"><label htmlFor="password" className="form-label">Senha</label><div className="password-wrap"><input id="password" autoComplete="current-password" type={mostrarSenha ? "text":"password"} className="form-control form-control-lg" value={password} onChange={(e)=>setPassword(e.target.value)} required /><button type="button" className="password-toggle" aria-label={mostrarSenha ? "Ocultar senha":"Mostrar senha"} onClick={()=>setMostrarSenha((v)=>!v)}><i className={`bi ${mostrarSenha ? "bi-eye-slash":"bi-eye"}`} /></button></div></div>
            <button type="submit" className="btn btn-primary w-100 login-submit" disabled={enviando}>{enviando ? <><span className="spinner-border spinner-border-sm me-2" />Entrando...</> : <>Entrar <i className="bi bi-arrow-right ms-2" /></>}</button>
          </form>
        </div>
      </section>
    </div>
  );
}
