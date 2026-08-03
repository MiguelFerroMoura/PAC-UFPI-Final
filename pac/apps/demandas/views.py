from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .constants import pode_transicionar_status
from .forms import DemandaForm, ItemDemandaForm
from .models import Demanda, ItemDemanda, StatusDemanda

@login_required
def demanda_list(request):
    qs = Demanda.objects.select_related("unidade", "usuario").prefetch_related("itens")

    if not request.user.is_admin_user:
        qs = qs.filter(usuario=request.user)

    return render(request, "demandas/list.html", {"demandas": qs})

@login_required
def demanda_create(request):
    if request.method == "POST":
        form = DemandaForm(request.POST)

        if form.is_valid():
            demanda = form.save(commit=False)
            demanda.usuario = request.user
            demanda.unidade = getattr(request.user, "unidade", None)
            
            if not demanda.unidade:
                messages.error(request, "Seu usuário não possui uma unidade vinculada. Contate o administrador.")
                return render(request, "crud/form.html", {"form": form, "titulo": "Nova Demanda"})
                
            demanda.save()

            messages.success(request, "Demanda criada. Agora adicione os itens.")
            return redirect("demandas:detalhe", pk=demanda.pk)
    else:
        form = DemandaForm(initial={"ano_referencia": timezone.now().year + 1})

    return render(request, "crud/form.html", {"form": form, "titulo": "Nova Demanda"})

@login_required
def demanda_detail(request, pk):
    demanda = get_object_or_404(
        Demanda.objects.select_related("unidade", "usuario").prefetch_related("itens"),
        pk=pk,
    )
    if not request.user.is_admin_user and demanda.usuario != request.user:
        messages.error(request, "Você não tem permissão para ver esta demanda.")
        return redirect("demandas:lista")
        
    return render(request, "demandas/detail.html", {"demanda": demanda})

@login_required
def demanda_update(request, pk):
    demanda = get_object_or_404(Demanda, pk=pk)

    if not request.user.is_admin_user and demanda.usuario != request.user:
        messages.error(request, "Você não tem permissão para editar esta demanda.")
        return redirect("demandas:lista")

    if demanda.status != StatusDemanda.RASCUNHO:
        messages.error(request, "Somente demandas em rascunho podem ser editadas.")
        return redirect("demandas:detalhe", pk=pk)

    form = DemandaForm(request.POST or None, instance=demanda)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Demanda atualizada.")
        return redirect("demandas:detalhe", pk=pk)

    return render(request, "crud/form.html", {"form": form, "titulo": "Editar Demanda"})

@login_required
def item_create(request, demanda_pk):
    demanda = get_object_or_404(Demanda, pk=demanda_pk)
    
    if not request.user.is_admin_user and demanda.usuario != request.user:
        messages.error(request, "Você não tem permissão para adicionar itens nesta demanda.")
        return redirect("demandas:lista")

    form = ItemDemandaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.demanda = demanda
        item.status = StatusDemanda.RASCUNHO
        item.valor_total = Decimal(item.quantidade) * item.valor_estimado
        item.save()

        messages.success(request, "Item adicionado.")
        return redirect("demandas:detalhe", pk=demanda.pk)

    return render(request, "crud/form.html", {"form": form, "titulo": "Adicionar Item"})

@login_required
def item_update(request, pk):
    item = get_object_or_404(ItemDemanda, pk=pk)

    if not request.user.is_admin_user and item.demanda.usuario != request.user:
        messages.error(request, "Você não tem permissão para editar este item.")
        return redirect("demandas:lista")

    if item.demanda.status != StatusDemanda.RASCUNHO and item.status != StatusDemanda.DEVOLVIDA:
        messages.error(request, "Itens só podem ser editados enquanto a demanda estiver em rascunho ou devolvidos.")
        return redirect("demandas:detalhe", pk=item.demanda_id)

    form = ItemDemandaForm(request.POST or None, instance=item)

    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.valor_total = Decimal(item.quantidade) * item.valor_estimado
        item.save()

        messages.success(request, "Item atualizado.")
        return redirect("demandas:detalhe", pk=item.demanda_id)

    return render(request, "crud/form.html", {"form": form, "titulo": "Editar Item"})

@login_required
def demanda_enviar(request, pk):
    demanda = get_object_or_404(Demanda, pk=pk)

    if not request.user.is_admin_user and demanda.usuario != request.user:
        messages.error(request, "Você não tem permissão para enviar esta demanda.")
        return redirect("demandas:lista")

    if not demanda.itens.exists():
        messages.error(request, "Adicione pelo menos um item antes de enviar.")
        return redirect("demandas:detalhe", pk=pk)

    if not pode_transicionar_status(demanda.status, StatusDemanda.AGUARDANDO_VALIDACAO):
        messages.error(request, f"Transição inválida de {demanda.status} para {StatusDemanda.AGUARDANDO_VALIDACAO}.")
        return redirect("demandas:detalhe", pk=pk)

    demanda.status = StatusDemanda.AGUARDANDO_VALIDACAO
    demanda.enviada_em = timezone.now()
    demanda.save(update_fields=["status", "enviada_em", "atualizado_em"])
    demanda.itens.update(status=StatusDemanda.AGUARDANDO_VALIDACAO)

    messages.success(request, "Demanda enviada para validação.")
    return redirect("demandas:detalhe", pk=pk)
