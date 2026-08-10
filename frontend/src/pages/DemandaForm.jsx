import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import Spinner from "../components/Spinner";

export default function DemandaForm() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();
  const [anoReferencia, setAnoReferencia] = useState(new Date().getFullYear() + 1);
  const [observacao, setObservacao] = useState("");
  const [carregando, setCarregando] = useState(editando);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (!editando) return;
    api.getDemanda(id).then((d) => { setAnoReferencia(d.ano_referencia); setObservacao(d.observacao || ""); })
      .catch((e) => setErro(e.message)).finally(() => setCarregando(false));
  }, [id, editando]);

  async function handleSubmit(e) {
    e.preventDefault(); setErro(""); setEnviando(true);
    try {
      const payload = { ano_referencia: Number(anoReferencia), observacao };
      const demanda = editando ? await api.updateDemanda(id, payload) : await api.createDemanda(payload);
      navigate(`/demandas/${demanda.id}`);
    } catch (err) { setErro(err.message || "Não foi possível salvar a demanda."); }
    finally { setEnviando(false); }
  }

  if (carregando) return <Spinner />;

  return (
    <div className="form-shell">
      <div className="page-head">
        <div><Link to={editando ? `/demandas/${id}` : "/demandas"} className="text-decoration-none small text-primary"><i className="bi bi-arrow-left me-1" />Voltar</Link><span className="page-kicker d-block mt-2">Planejamento</span><h1>{editando ? "Editar demanda" : "Nova demanda"}</h1><p>Informe o ano de referência e os dados gerais da solicitação.</p></div>
      </div>
      <form className="form-card" onSubmit={handleSubmit}>
        {erro && <div className="alert alert-danger"><i className="bi bi-exclamation-triangle me-2" />{erro}</div>}
        <div className="section-divider"><i className="bi bi-file-earmark-text me-2 text-primary" />Dados gerais</div>
        <div className="row g-3">
          <div className="col-md-5"><label htmlFor="ano" className="form-label">Ano de referência</label><input id="ano" type="number" min="2020" max="2100" className="form-control" value={anoReferencia} onChange={(e)=>setAnoReferencia(e.target.value)} required /><div className="form-text small">Ano em que a contratação está prevista.</div></div>
          <div className="col-12"><label htmlFor="obs" className="form-label">Observação <span className="text-muted fw-normal">(opcional)</span></label><textarea id="obs" className="form-control" rows={5} maxLength={1000} value={observacao} onChange={(e)=>setObservacao(e.target.value)} placeholder="Inclua informações que ajudem a identificar o contexto da demanda." /></div>
        </div>
        <div className="form-actions"><Link to={editando ? `/demandas/${id}` : "/demandas"} className="btn btn-light">Cancelar</Link><button className="btn btn-primary" disabled={enviando}>{enviando ? <><span className="spinner-border spinner-border-sm me-2" />Salvando...</> : <><i className="bi bi-check2 me-2" />Salvar</>}</button></div>
      </form>
    </div>
  );
}
