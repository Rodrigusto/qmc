from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from .models import Sale, SaleItem
from purchases.models import Stock
import datetime


def create_sale(data: dict, items: list) -> Sale:
    """
    Cria venda com itens, calcula totais e deduz estoque.
    Tudo em transação atômica — ou salva tudo ou nada.
    """
    with transaction.atomic():
        sale = Sale.objects.create(**data)

        for item in items:
            if not item.get('product_id') or not item.get('quantity'):
                continue
            SaleItem.objects.create(
                sale=sale,
                product_id=item['product_id'],
                quantity=int(item['quantity']),
                unit_price=Decimal(str(item['unit_price'])),
            )

        sale.recalculate_totals()
        sale.save()

        if sale.status == Sale.Status.CONFIRMED:
            _deduct_stock(sale)

    return sale


def cancel_sale(sale: Sale) -> Sale:
    """
    Cancela uma venda e estorna os ingredientes no estoque.
    Só estorna se a venda estava confirmada ou entregue.
    """
    with transaction.atomic():
        if sale.status in (Sale.Status.CONFIRMED, Sale.Status.DELIVERED):
            _restore_stock(sale)

        sale.status = Sale.Status.CANCELLED
        sale.save()

    return sale


def _deduct_stock(sale: Sale):
    """Deduz ingredientes do estoque para cada item da venda."""
    for item in sale.items.select_related('product').all():
        for recipe_item in item.product.recipe_items.select_related('ingredient').all():
            needed = Decimal(str(recipe_item.quantity)) * Decimal(str(item.quantity))
            try:
                stock = Stock.objects.get(ingredient=recipe_item.ingredient)
                stock.quantity = max(Decimal('0'), Decimal(str(stock.quantity)) - needed)
                stock.save()
            except Stock.DoesNotExist:
                pass


def _restore_stock(sale: Sale):
    """Estorna ingredientes no estoque ao cancelar uma venda."""
    for item in sale.items.select_related('product').all():
        for recipe_item in item.product.recipe_items.select_related('ingredient').all():
            to_restore = Decimal(str(recipe_item.quantity)) * Decimal(str(item.quantity))
            stock, _   = Stock.objects.get_or_create(ingredient=recipe_item.ingredient)
            stock.quantity = Decimal(str(stock.quantity)) + to_restore
            stock.save()


def get_monthly_summary(month: int, year: int) -> dict:
    """Resumo de vendas do mês para comparar com a previsão."""
    from calculations.models import SalesForecast

    sales = Sale.objects.filter(
        date__month=month,
        date__year=year,
    ).exclude(status=Sale.Status.CANCELLED)

    items_qs = SaleItem.objects.filter(
        sale__date__month=month,
        sale__date__year=year,
    ).exclude(
        sale__status=Sale.Status.CANCELLED
    ).values(
        'product__id', 'product__name'
    ).annotate(
        total_units=Sum('quantity'),
        total_revenue=Sum('subtotal'),
    )

    forecasts = {
        str(f.product_id): f.expected_units
        for f in SalesForecast.objects.filter(month=month, year=year)
    }

    products_data = []
    for item in items_qs:
        pid       = str(item['product__id'])
        previsto  = forecasts.get(pid, 0)
        realizado = item['total_units']
        pct       = round(realizado / previsto * 100, 1) if previsto else 0
        products_data.append({
            'product_name':  item['product__name'],
            'previsto':      previsto,
            'realizado':     realizado,
            'percentual':    pct,
            'total_revenue': item['total_revenue'] or Decimal('0'),
        })

    return {
        'total_sales':   sales.count(),
        'total_revenue': sales.aggregate(t=Sum('total'))['t'] or Decimal('0'),
        'products':      products_data,
        'month':         month,
        'year':          year,
    }