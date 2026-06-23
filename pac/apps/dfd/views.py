from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import DFD
from apps.demandas.models import ItemDemanda, StatusDemanda

@login_required
def dfd_list(request):
    # Somente admins e admin_master veem DFDs por padrão?
    # No PAC UFPI, DFDs costumam ser públicos ou para acompanhamento
    qs = DFD.objects.select_related("grupo", "criado_por").prefetch_related("itens_demanda")
    return render(request, "dfd/list.html", {"dfds": qs})

@login_required
def dfd_detail(request, pk):
    dfd = get_object_or_404(DFD.objects.prefetch_related("itens_demanda"), pk=pk)
    total = sum(item.valor_total for item in dfd.itens_demanda.all())
    return render(request, "dfd/detail.html", {"dfd": dfd, "total_dfd": total})

@login_required
def dfd_consolidar(request):
    """
    View para consolidar itens VALIDADOS em um DFD.
    """
    if not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect("home")
        
    # Itens validados que ainda não estão em nenhum DFD
    itens_pendentes = ItemDemanda.objects.filter(
        status=StatusDemanda.VALIDADA
    ).exclude(dfds__isnull=False).select_related("demanda", "demanda__unidade")
    
    if request.method == "POST":
        # Lógica de criação de DFD a partir dos itens selecionados
        item_ids = request.POST.getlist("itens")
        grupo_id = request.POST.get("grupo")
        numero_dfd = request.POST.get("numero")
        
        if not item_ids or not grupo_id or not numero_dfd:
            messages.error(request, "Preencha todos os campos e selecione ao menos um item.")
        else:
            dfd = DFD.objects.create(
                numero=numero_dfd,
                grupo_id=grupo_id,
                criado_por=request.user
            )
            dfd.itens_demanda.set(item_ids)
            # Atualiza status dos itens para consolidado
            ItemDemanda.objects.filter(id__in=item_ids).update(status=StatusDemanda.CONSOLIDADA)
            
            messages.success(request, f"DFD {dfd.numero} criado com sucesso.")
            return redirect("dfds:detalhe", pk=dfd.pk)

    from apps.grupos_contratacao.models import GrupoContratacao
    grupos = GrupoContratacao.objects.filter(ativo=True)
    return render(request, "dfd/consolidar.html", {"itens": itens_pendentes, "grupos": grupos})
