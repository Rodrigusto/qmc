from decimal import Decimal
from django.db import transaction
from .models import Purchase, PurchaseItem, Stock, Supplier
from ingredients.models import Ingredient


def create_purchase(supplier_id: str, date: str, note: str, items: list) -> Purchase:
    """
    Cria uma compra com seus itens dentro de uma transação atômica.
    Se qualquer item falhar, nada é salvo.

    items: list de dicts com ingredient_id, quantity, total_price
    """
    with transaction.atomic():
        purchase = Purchase.objects.create(
            supplier_id=supplier_id,
            date=date,
            note=note,
        )

        for item in items:
            if not item.get('ingredient_id') or not item.get('quantity'):
                continue

            quantity    = Decimal(str(item['quantity']))
            total_price = Decimal(str(item['total_price']))

            PurchaseItem.objects.create(
                purchase=purchase,
                ingredient_id=item['ingredient_id'],
                quantity=quantity,
                total_price=total_price,
            )

            _update_stock_and_cost(
                ingredient_id=item['ingredient_id'],
                quantity=quantity,
                total_price=total_price,
            )

        return purchase


def cancel_purchase(purchase: Purchase) -> Purchase:
    """
    Cancela uma compra e estorna o estoque e custo médio.
    Usa soft delete — apenas desativa o registro.
    """
    with transaction.atomic():
        for item in purchase.items.all():
            _revert_stock_and_cost(
                ingredient_id=str(item.ingredient_id),
                quantity=Decimal(str(item.quantity)),
                total_price=Decimal(str(item.total_price)),
            )

        purchase.is_active = False
        purchase.save()

    return purchase


def _update_stock_and_cost(ingredient_id: str, quantity: Decimal, total_price: Decimal):
    """
    Atualiza saldo e custo médio ponderado de um ingrediente.
    Privado — chamado apenas por create_purchase.
    """
    stock, _ = Stock.objects.get_or_create(ingredient_id=ingredient_id)

    saldo_atual = Decimal(str(stock.quantity))
    custo_atual = Decimal(str(stock.ingredient.cost_per_unit))
    custo_novo  = total_price / quantity if quantity > 0 else Decimal('0')
    novo_saldo  = saldo_atual + quantity

    novo_custo_medio = (
        (saldo_atual * custo_atual) + (quantity * custo_novo)
    ) / novo_saldo if novo_saldo > 0 else custo_novo

    stock.quantity = novo_saldo
    stock.save()

    Ingredient.objects.filter(pk=ingredient_id).update(
        cost_per_unit=novo_custo_medio
    )


def _revert_stock_and_cost(ingredient_id: str, quantity: Decimal, total_price: Decimal):
    """
    Reverte o efeito de um item no estoque e custo médio.
    Chamado ao cancelar uma compra.
    """
    try:
        stock = Stock.objects.get(ingredient_id=ingredient_id)
    except Stock.DoesNotExist:
        return

    saldo_atual = Decimal(str(stock.quantity))
    custo_atual = Decimal(str(stock.ingredient.cost_per_unit))
    custo_item  = total_price / quantity if quantity > 0 else Decimal('0')
    novo_saldo  = max(Decimal('0'), saldo_atual - quantity)

    # recalcula custo médio revertendo a entrada
    if novo_saldo > 0:
        valor_total_atual  = saldo_atual * custo_atual
        valor_item         = quantity * custo_item
        novo_custo_medio   = (valor_total_atual - valor_item) / novo_saldo
    else:
        novo_custo_medio = Decimal('0')

    stock.quantity = novo_saldo
    stock.save()

    Ingredient.objects.filter(pk=ingredient_id).update(
        cost_per_unit=max(Decimal('0'), novo_custo_medio)
    )