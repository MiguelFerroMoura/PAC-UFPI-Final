from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from apps.demandas.models import ItemDemanda, StatusDemanda
from .models import Validacao, TipoAcao

@login_required
def lista_pendentes(request):
    if not request.user.is_staff:
        messages.error(request, "Acesso restrito a administradores.")
        return redirect("home")
        
    # Itens aguardando validação
    itens = ItemDemanda.objects.filter(
        status=StatusDemanda.AGUARDANDO_VALIDACAO
    ).select_related("demanda", "demanda__unidade", "demanda__usuario")
    
    return render(request, "validacoes/lista_pendentes.html", {"itens": itens})

@login_required
def validar_item(request, item_pk):
    if not request.user.is_staff:
        messages.error(request, "Acesso restrito a administradores.")
        return redirect("home")
        
    item = get_object_or_404(ItemDemanda, pk=item_pk)
    
    if request.method == "POST":
        acao = request.POST.get("acao")
        comentario = request.POST.get("comentario", "")
        
        if acao == "validar":
            item.status = StatusDemanda.VALIDADA
            Validacao.objects.create(
                item=item,
                usuario=request.user,
                acao=TipoAcao.VALIDADO,
                comentario=comentario
            )
            messages.success(request, f"Item '{item.nome}' validado.")
        elif acao == "devolver":
            if not comentario:
                messages.error(request, "É obrigatório informar um comentário para devolução.")
                return render(request, "validacoes/decisao.html", {"item": item})
                
            item.status = StatusDemanda.DEVOLVIDA
            Validacao.objects.create(
                item=item,
                usuario=request.user,
                acao=TipoAcao.DEVOLVIDO,
                comentario=comentario
            )
            messages.warning(request, f"Item '{item.nome}' devolvido para correção.")
            
        item.save()
        
        return redirect("validacoes:lista_pendentes")

    return render(request, "validacoes/decisao.html", {"item": item})
