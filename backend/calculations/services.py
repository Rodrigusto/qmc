from decimal import Decimal
from django.db.models import Sum
from .models import FixedCost, Expense, SalesForecast, CostCalculation
import datetime


def calculate_ggf(month: int, year: int) -> dict:
    """
    Calcula o GGF (Gasto Geral de Funcionamento) por produto.

    Fórmula:
        1. GGF total = custos fixos ativos + despesas do mês
        2. Faturamento previsto por produto = unidades × custo ingredientes
        3. Proporção do produto = fat. produto ÷ fat. total
        4. GGF do produto = (GGF total × proporção) ÷ unidades previstas
    """

    # 1. GGF total do mês
    total_fixed = FixedCost.objects.filter(is_active=True).aggregate(
        total=Sum('monthly_amount')
    )['total'] or Decimal('0')

    total_expenses = Expense.objects.filter(
        date__month=month,
        date__year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    ggf_total = Decimal(str(total_fixed)) + Decimal(str(total_expenses))

    # 2. Previsões do mês
    forecasts = SalesForecast.objects.filter(
        month=month, year=year
    ).select_related('product').prefetch_related(
        'product__recipe_items__ingredient'
    )

    if not forecasts.exists():
        return {
            'ggf_total':    ggf_total,
            'total_fixed':  total_fixed,
            'total_expenses': total_expenses,
            'products':     [],
            'error': 'Nenhuma previsão de vendas cadastrada para este período.'
        }

    # 3. Faturamento previsto total (base do rateio proporcional)
    product_data = []
    faturamento_total = Decimal('0')

    for forecast in forecasts:
        ingredient_cost  = Decimal(str(forecast.product.ingredient_cost))
        units            = Decimal(str(forecast.expected_units))
        faturamento      = ingredient_cost * units
        faturamento_total += faturamento
        product_data.append({
            'forecast':        forecast,
            'ingredient_cost': ingredient_cost,
            'units':           units,
            'faturamento':     faturamento,
        })

    # 4. GGF por produto
    results = []
    for item in product_data:
        if faturamento_total > 0:
            proporcao = item['faturamento'] / faturamento_total
        else:
            proporcao = Decimal('1') / Decimal(str(len(product_data)))

        ggf_produto     = (ggf_total * proporcao) / item['units']
        custo_total     = item['ingredient_cost'] + ggf_produto

        results.append({
            'product':         item['forecast'].product,
            'expected_units':  item['units'],
            'ingredient_cost': item['ingredient_cost'],
            'faturamento':     item['faturamento'],
            'proporcao':       proporcao * 100,   # em %
            'ggf_per_unit':    ggf_produto,
            'total_cost':      custo_total,
        })

    return {
        'ggf_total':        ggf_total,
        'total_fixed':      total_fixed,
        'total_expenses':   total_expenses,
        'faturamento_total': faturamento_total,
        'products':         results,
        'error':            None,
    }


def save_calculations(month: int, year: int) -> list:
    """
    Roda o GGF e salva um CostCalculation para cada produto.
    Substitui cálculos anteriores do mesmo mês/ano.
    """
    data = calculate_ggf(month, year)
    if data['error']:
        return []

    saved = []
    for item in data['products']:
        # remove cálculo anterior do mesmo produto/mês/ano se existir
        CostCalculation.objects.filter(
            product=item['product'],
            created_at__month=month,
            created_at__year=year,
        ).delete()

        calc = CostCalculation.objects.create(
            product=item['product'],
            expected_monthly_sales=int(item['expected_units']),
            ingredient_cost=item['ingredient_cost'],
            fixed_cost_share=item['ggf_per_unit'],
            expense_share=Decimal('0'),   # já embutido no GGF
            total_cost=item['total_cost'],
        )
        saved.append(calc)

    return saved