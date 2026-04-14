from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Purchase, Stock, Supplier
from .services import create_purchase, cancel_purchase
from ingredients.models import Ingredient
import datetime


def purchase_list(request):
    purchases = Purchase.objects.filter(is_active=True).select_related(
        'supplier'
    ).prefetch_related('items__ingredient')
    return render(request, 'purchases/list.html', {'purchases': purchases})


def purchase_new(request):
    suppliers   = Supplier.objects.filter(is_active=True)
    ingredients = Ingredient.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredient[]')
        quantities     = request.POST.getlist('quantity[]')
        total_prices   = request.POST.getlist('total_price[]')

        items = [
            {'ingredient_id': i, 'quantity': q, 'total_price': p}
            for i, q, p in zip(ingredient_ids, quantities, total_prices)
            if i and q and p
        ]

        if not items:
            messages.error(request, 'Adicione ao menos um item à compra.')
        else:
            try:
                create_purchase(
                    supplier_id=request.POST.get('supplier'),
                    date=request.POST.get('date'),
                    note=request.POST.get('note', ''),
                    items=items,
                )
                messages.success(request, 'Compra registrada e estoque atualizado!')
                return redirect('purchases:list')
            except Exception as e:
                messages.error(request, f'Erro ao registrar compra: {e}')

    return render(request, 'purchases/new.html', {
        'suppliers':   suppliers,
        'ingredients': ingredients,
        'today':       datetime.date.today().isoformat(),
    })


def purchase_cancel(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, is_active=True)
    if request.method == 'POST':
        try:
            cancel_purchase(purchase)
            messages.success(request, 'Compra cancelada e estoque estornado.')
        except Exception as e:
            messages.error(request, f'Erro ao cancelar: {e}')
    return redirect('purchases:list')


def stock_list(request):
    stocks = Stock.objects.select_related('ingredient').order_by('ingredient__name')
    return render(request, 'purchases/stock.html', {'stocks': stocks})


def supplier_list(request):
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Supplier.objects.create(
                name=request.POST.get('name'),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                note=request.POST.get('note', ''),
            )
            messages.success(request, 'Fornecedor cadastrado!')

        elif action == 'toggle':
            pk  = request.POST.get('pk')
            sup = get_object_or_404(Supplier, pk=pk)
            sup.is_active = not sup.is_active
            sup.save()
            status = 'ativado' if sup.is_active else 'desativado'
            messages.success(request, f'Fornecedor {status}.')

        return redirect('purchases:suppliers')

    return render(request, 'purchases/suppliers.html', {'suppliers': suppliers})