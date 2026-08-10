import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";

const CAMPOS_INICIAIS = { tipo:"material",nome:"",descricao:"",unidade_medida:"",quantidade:1,valor_estimado:"",data_prevista:"",prioridade:"media",justificativa_prioridade:"",justificativa_necessidade:"",indicacao_orcamentaria:"" };

export default function ItemForm() {
  const { id } = useParams(); const navigate = useNavigate();
  const [form,setForm]=useState(CAMPOS_INICIAIS); const [erro,setErro]=useState(""); const [enviando,setEnviando]=useState(false);
  const atualizar=(campo,valor)=>setForm((atual)=>({...atual,[campo]:valor}));
  async function handleSubmit(e){
    e.preventDefault();setErro("");setEnviando(true);
    try{await api.addItem(id,{...form,quantidade:Number(form.quantidade),valor_estimado:Number(form.valor_estimado)});navigate(`/demandas/${id}`);}
    catch(err){setErro(err.message||"Não foi possível adicionar o item.");}finally{setEnviando(false);}
  }
  const Field=({id,label,children,help})=><div className="mb-3"><label htmlFor={id} className="form-label">{label}</label>{children}{help&&<div className="form-text small">{help}</div>}</div>;
  return <div className="form-shell">
    <div className="page-head"><div><Link to={`/demandas/${id}`} className="text-decoration-none small text-primary"><i className="bi bi-arrow-left me-1"/>Voltar para demanda</Link><span className="page-kicker d-block mt-2">Itens</span><h1>Adicionar item</h1><p>Descreva o material ou serviço que será incluído na demanda.</p></div></div>
    <form className="form-card" onSubmit={handleSubmit}>
      {erro&&<div className="alert alert-danger"><i className="bi bi-exclamation-triangle me-2"/>{erro}</div>}
      <div className="section-divider"><i className="bi bi-box-seam me-2 text-primary"/>Identificação</div>
      <div className="row g-3">
        <div className="col-md-3"><Field id="tipo" label="Tipo"><select id="tipo" className="form-select" value={form.tipo} onChange={e=>atualizar("tipo",e.target.value)}><option value="material">Material</option><option value="servico">Serviço</option></select></Field></div>
        <div className="col-md-9"><Field id="nome" label="Nome"><input id="nome" className="form-control" value={form.nome} onChange={e=>atualizar("nome",e.target.value)} required /></Field></div>
        <div className="col-12"><Field id="descricao" label="Descrição"><textarea id="descricao" className="form-control" rows={3} value={form.descricao} onChange={e=>atualizar("descricao",e.target.value)} required /></Field></div>
        <div className="col-md-4"><Field id="unidade_medida" label="Unidade de medida"><input id="unidade_medida" className="form-control" placeholder="Ex.: unidade, serviço" value={form.unidade_medida} onChange={e=>atualizar("unidade_medida",e.target.value)} required /></Field></div>
        <div className="col-md-4"><Field id="quantidade" label="Quantidade"><input id="quantidade" type="number" min="1" step="1" className="form-control" value={form.quantidade} onChange={e=>atualizar("quantidade",e.target.value)} required /></Field></div>
        <div className="col-md-4"><Field id="valor_estimado" label="Valor estimado unitário"><input id="valor_estimado" type="number" min="0" step="0.01" className="form-control" value={form.valor_estimado} onChange={e=>atualizar("valor_estimado",e.target.value)} required /></Field></div>
      </div>
      <div className="section-divider"><i className="bi bi-calendar3 me-2 text-primary"/>Planejamento</div>
      <div className="row g-3">
        <div className="col-md-4"><Field id="data_prevista" label="Data prevista"><input id="data_prevista" type="date" className="form-control" value={form.data_prevista} onChange={e=>atualizar("data_prevista",e.target.value)} required /></Field></div>
        <div className="col-md-4"><Field id="prioridade" label="Prioridade"><select id="prioridade" className="form-select" value={form.prioridade} onChange={e=>atualizar("prioridade",e.target.value)}><option value="baixa">Baixa</option><option value="media">Média</option><option value="alta">Alta</option><option value="critica">Crítica</option></select></Field></div>
        <div className="col-md-4"><Field id="indicacao_orcamentaria" label="Indicação orçamentária"><input id="indicacao_orcamentaria" className="form-control" value={form.indicacao_orcamentaria} onChange={e=>atualizar("indicacao_orcamentaria",e.target.value)} required /></Field></div>
        <div className="col-md-6"><Field id="justificativa_prioridade" label="Justificativa da prioridade"><textarea id="justificativa_prioridade" className="form-control" rows={4} value={form.justificativa_prioridade} onChange={e=>atualizar("justificativa_prioridade",e.target.value)} required /></Field></div>
        <div className="col-md-6"><Field id="justificativa_necessidade" label="Justificativa da necessidade"><textarea id="justificativa_necessidade" className="form-control" rows={4} value={form.justificativa_necessidade} onChange={e=>atualizar("justificativa_necessidade",e.target.value)} required /></Field></div>
      </div>
      <div className="form-actions"><Link to={`/demandas/${id}`} className="btn btn-light">Cancelar</Link><button className="btn btn-primary" disabled={enviando}>{enviando?<><span className="spinner-border spinner-border-sm me-2"/>Salvando...</>:<><i className="bi bi-check2 me-2"/>Adicionar item</>}</button></div>
    </form>
  </div>;
}
