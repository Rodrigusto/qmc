from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Purchase, PurchaseItem, Stock, Supplier
from ingredients.models import Ingredient
import datetime


def purchase_list(request):
    purchases = Purchase.objects.select_related('supplier').prefetch_related('items')
    return render(request, 'purchases/list.html', {'purchases': purchases})


def purchase_new(request):
    suppliers   = Supplier.objects.filter(is_active=True)
    ingredients = Ingredient.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        date        = request.POST.get('date')
        note        = request.POST.get('note', '')

        # coleta os itens enviados pelo formulário dinâmico
        ingredient_ids = request.POST.getlist('ingredient[]')
        quantities     = request.POST.getlist('quantity[]')
        total_prices   = request.POST.getlist('total_price[]')

        # valida se tem ao menos um item
        valid_items = [
            (i, q, p)
            for i, q, p in zip(ingredient_ids, quantities, total_prices)
            if i and q and p
        ]

        if not valid_items:
            messages.error(request, 'Adicione ao menos um item à compra.')
        else:
            purchase = Purchase.objects.create(
                supplier_id=supplier_id,
                date=date,
                note=note,
            )
            for ingredient_id, quantity, total_price in valid_items:
                PurchaseItem.objects.create(
                    purchase=purchase,
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                    total_price=total_price,
                )

            messages.success(request, 'Compra registrada e estoque atualizado!')
            return redirect('purchases:list')

    context = {
        'suppliers':   suppliers,
        'ingredients': ingredients,
        'today':       datetime.date.today().isoformat(),
    }
    return render(request, 'purchases/new.html', context)


def stock_list(request):
    stocks = Stock.objects.select_related('ingredient').order_by('ingredient__name')
    return render(request, 'purchases/stock.html', {'stocks': stocks})