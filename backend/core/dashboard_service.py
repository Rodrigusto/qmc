from decimal import Decimal
from django.db.models import Sum, Avg
import datetime
import json

def get_dashboard_data(user) -> dict:
    from sales.models import Sale, SaleItem
    from purchases.models import Stock
    from products.models import Product
    from calculations.models import FixedCost, Expense, SalesForecast

    today = datetime.date.today()
    month = today.month
    year  = today.year

    # ── Vendas ──────────────────────────────────────────
    sales_today = Sale.objects.filter(
        date=today
    ).exclude(status='cancelled')

    sales_month = Sale.objects.filter(
        date__month=month, date__year=year
    ).exclude(status='cancelled')

    faturamento_hoje = sales_today.aggregate(
        t=Sum('total')
    )['t'] or Decimal('0')

    faturamento_mes = sales_month.aggregate(
        t=Sum('total')
    )['t'] or Decimal('0')

    qtd_vendas_hoje = sales_today.count()

    ticket_medio = sales_today.aggregate(
        avg=Avg('total')
    )['avg'] or Decimal('0')

    # ── Últimas vendas ───────────────────────────────────
    ultimas_vendas = Sale.objects.filter(
    ).exclude(status='cancelled').select_related(
        'channel', 'customer'
    ).prefetch_related('items__product').order_by('-created_at')[:8]

    # ── Vendas da semana (últimos 7 dias) ────────────────
    semana = []
    for i in range(6, -1, -1):
        dia  = today - datetime.timedelta(days=i)
        fat  = Sale.objects.filter(date=dia
        ).exclude(status='cancelled').aggregate(
            t=Sum('total')
        )['t'] or Decimal('0')
        semana.append({
            'dia':   dia.strftime('%a'),
            'data':  dia.strftime('%d/%m'),
            'total': float(fat),
        })

    # ── Produtos mais vendidos ───────────────────────────
    mais_vendidos = SaleItem.objects.filter(
        sale__date__month=month,
        sale__date__year=year,
    ).exclude(sale__status='cancelled').values(
        'product__name'
    ).annotate(
        total_units=Sum('quantity'),
        # total_revenue=Sum('subtotal'),
    ).order_by('-total_units')[:5]

    # ── Semáforo de produtos ─────────────────────────────
    products = Product.objects.filter(
        is_active=True
    ).prefetch_related('recipe_items__ingredient')

    semaforo_produtos = []
    for product in products:
        custo        = product.ingredient_cost
        preco_venda  = product.sale_price or Decimal('0')

        if preco_venda > 0:
            lucro   = preco_venda - custo
            margem  = (lucro / preco_venda) * 100

            if margem >= 35:
                status = 'green'
                label  = 'Saudável'
            elif margem >= 20:
                status = 'yellow'
                label  = 'Atenção'
            else:
                status = 'red'
                label  = 'Crítico'
        else:
            lucro  = Decimal('0')
            margem = Decimal('0')
            status = 'gray'
            label  = 'Sem preço'

        semaforo_produtos.append({
            'name':   product.name,
            'custo':  custo,
            'preco':  preco_venda,
            'lucro':  lucro,
            'margem': margem,
            'status': status,
            'label':  label,
        })

    semaforo_produtos.sort(key=lambda x: x['margem'])

    # ── Estoque ──────────────────────────────────────────
    stocks = Stock.objects.filter().select_related('ingredient')

    estoque_alertas = []
    estoque_ok      = []
    for stock in stocks:
        item = {
            'name':     stock.ingredient.name,
            'quantity': stock.quantity,
            'unit':     stock.ingredient.get_unit_display(),
        }
        if stock.quantity <= 0:
            item['status'] = 'red'
            item['label']  = 'Esgotado'
            estoque_alertas.append(item)
        elif stock.is_low:
            item['status'] = 'yellow'
            item['label']  = 'Baixo'
            estoque_alertas.append(item)
        else:
            item['status'] = 'green'
            item['label']  = 'Ok'
            estoque_ok.append(item)

    # ── Saúde financeira ─────────────────────────────────
    total_fixos = FixedCost.objects.filter(
        is_active=True
    ).aggregate(t=Sum('monthly_amount'))['t'] or Decimal('0')

    total_despesas = Expense.objects.filter(
        date__month=month,
        date__year=year,
    ).aggregate(t=Sum('amount'))['t'] or Decimal('0')

    pct_fixos     = float(total_fixos / faturamento_mes * 100) if faturamento_mes > 0 else 0
    pct_despesas  = float(total_despesas / faturamento_mes * 100) if faturamento_mes > 0 else 0

    # semáforo saúde financeira
    def saude_pct(pct, limite_green, limite_yellow):
        if pct <= limite_green:  return 'green'
        if pct <= limite_yellow: return 'yellow'
        return 'red'

    saude_fixos    = saude_pct(pct_fixos,    30, 50)
    saude_despesas = saude_pct(pct_despesas, 10, 20)

    # ── Previsão vs Realizado ────────────────────────────
    forecasts = SalesForecast.objects.filter(
        month=month, year=year
    ).select_related('product')

    previsao_data = []
    for f in forecasts:
        vendido = SaleItem.objects.filter(
            product=f.product,
            sale__date__month=month,
            sale__date__year=year,
        ).exclude(sale__status='cancelled').aggregate(
            t=Sum('quantity')
        )['t'] or 0

        pct = float(vendido / f.expected_units * 100) if f.expected_units > 0 else 0

        if pct >= 80:   status = 'green'
        elif pct >= 50: status = 'yellow'
        else:           status = 'red'

        previsao_data.append({
            'product':   f.product.name,
            'previsto':  f.expected_units,
            'realizado': vendido,
            'pct':       round(pct, 1),
            'status':    status,
        })

    return {
        # KPIs
        'faturamento_hoje': faturamento_hoje,
        'faturamento_mes':  faturamento_mes,
        'qtd_vendas_hoje':  qtd_vendas_hoje,
        'ticket_medio':     ticket_medio,
        # semáforo
        'semaforo_produtos': semaforo_produtos,
        # estoque
        'estoque_alertas':  estoque_alertas,
        'estoque_ok':       estoque_ok,
        # financeiro
        'total_fixos':      total_fixos,
        'total_despesas':   total_despesas,
        'pct_fixos':        round(pct_fixos, 1),
        'pct_despesas':     round(pct_despesas, 1),
        'saude_fixos':      saude_fixos,
        'saude_despesas':   saude_despesas,
        # semana
        'semana':           semana,
        'semana_json':   json.dumps([d['total'] for d in semana]),
        'semana_labels': json.dumps([d['dia']   for d in semana]),
        # mais vendidos
        'mais_vendidos':    mais_vendidos,
        # previsão
        'previsao_data':    previsao_data,
        # últimas vendas
        'ultimas_vendas':   ultimas_vendas,
        # período
        'today':            today,
        'month':            month,
        'year':             year,
    }