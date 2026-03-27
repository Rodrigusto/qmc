from django.shortcuts import render
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
