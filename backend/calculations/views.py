from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CostCalculation, SalesForecast
from .services import calculate_ggf, save_calculations
from django.db.models import Sum
from .models import FixedCost, Expense, CostCalculation
from products.models import Product
import datetime


def calculation_list(request):
    calculations = CostCalculation.objects.select_related('product').order_by('-created_at')
    return render(request, 'calculations/list.html', {'calculations': calculations})


def calculation_new(request):
    products = Product.objects.filter(is_active=True)
    result = None
    selected_product = request.GET.get('product', '')

    if request.method == 'POST':
        product_id     = request.POST.get('product_id')
        expected_sales = int(request.POST.get('expected_monthly_sales', 1))
        selected_product = product_id

        product          = Product.objects.prefetch_related('recipe_items__ingredient').get(pk=product_id)
        ingredient_cost  = product.ingredient_cost

        total_fixed      = FixedCost.objects.filter(is_active=True).aggregate(total=Sum('monthly_amount'))['total'] or 0
        fixed_share      = total_fixed / expected_sales

        now              = datetime.date.today()
        total_expenses   = Expense.objects.filter(date__month=now.month, date__year=now.year).aggregate(total=Sum('amount'))['total'] or 0
        expense_share    = total_expenses / expected_sales

        total_cost = ingredient_cost + fixed_share + expense_share

        result = CostCalculation.objects.create(
            product=product,
            expected_monthly_sales=expected_sales,
            ingredient_cost=ingredient_cost,
            fixed_cost_share=fixed_share,
            expense_share=expense_share,
            total_cost=total_cost,
        )

    return render(request, 'calculations/new.html', {
        'products':         products,
        'result':           result,
        'selected_product': selected_product,
    })


def forecast_list(request):
    """Lista todas as previsões de vendas."""
    now       = datetime.date.today()
    forecasts = SalesForecast.objects.select_related('product').order_by('-year', '-month')
    return render(request, 'calculations/forecast_list.html', {
        'forecasts':    forecasts,
        'current_month': now.month,
        'current_year':  now.year,
    })


def forecast_new(request):
    """Cadastra previsão de vendas por produto."""
    products = Product.objects.filter(is_active=True)
    now      = datetime.date.today()

    if request.method == 'POST':
        month       = int(request.POST.get('month'))
        year        = int(request.POST.get('year'))
        product_ids = request.POST.getlist('product_id[]')
        units_list  = request.POST.getlist('expected_units[]')

        saved = 0
        for product_id, units in zip(product_ids, units_list):
            if product_id and units:
                SalesForecast.objects.update_or_create(
                    product_id=product_id,
                    month=month,
                    year=year,
                    defaults={'expected_units': int(units)}
                )
                saved += 1

        messages.success(request, f'{saved} previsão(ões) salva(s) com sucesso!')
        return redirect('calculations:forecast_list')

    return render(request, 'calculations/forecast_new.html', {
        'products':      products,
        'current_month': now.month,
        'current_year':  now.year,
    })


def ggf_dashboard(request):
    """Tela principal do GGF — mostra o cálculo do mês selecionado."""
    now   = datetime.date.today()
    month = int(request.GET.get('month', now.month))
    year  = int(request.GET.get('year',  now.year))

    data = calculate_ggf(month, year)

    if request.method == 'POST':
        saved = save_calculations(month, year)
        if saved:
            messages.success(request, f'Cálculo salvo para {len(saved)} produto(s)!')
        return redirect('calculations:ggf')

    months = [(i, datetime.date(2000, i, 1).strftime('%B')) for i in range(1, 13)]

    return render(request, 'calculations/ggf.html', {
        'data':          data,
        'month':         month,
        'year':          year,
        'months':        months,
        'current_year':  now.year,
    })