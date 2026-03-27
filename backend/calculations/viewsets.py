from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import FixedCost, Expense, CostCalculation
from .serializers import FixedCostSerializer, ExpenseSerializer, CostCalculationSerializer
from products.models import Product
import datetime


class FixedCostViewSet(viewsets.ModelViewSet):
    queryset         = FixedCost.objects.all()
    serializer_class = FixedCostSerializer
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['name', 'category']

    def get_queryset(self):
        return FixedCost.objects.filter(is_active=True)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset         = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        qs    = Expense.objects.all()
        month = self.request.query_params.get('month')
        year  = self.request.query_params.get('year')
        if month and year:
            qs = qs.filter(date__month=month, date__year=year)
        return qs


class CostCalculationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = CostCalculation.objects.all()
    serializer_class = CostCalculationSerializer

    def get_queryset(self):
        return CostCalculation.objects.select_related('product')

    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate(self, request):
        product_id     = request.data.get('product_id')
        expected_sales = request.data.get('expected_monthly_sales')

        if not product_id or not expected_sales:
            return Response(
                {'error': 'product_id e expected_monthly_sales são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.prefetch_related(
                'recipe_items__ingredient'
            ).get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Produto não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        expected_sales  = int(expected_sales)
        ingredient_cost = product.ingredient_cost

        total_fixed = FixedCost.objects.filter(is_active=True).aggregate(
            total=Sum('monthly_amount')
        )['total'] or 0
        fixed_cost_share = total_fixed / expected_sales

        now = datetime.date.today()
        total_expenses = Expense.objects.filter(
            date__month=now.month,
            date__year=now.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        expense_share = total_expenses / expected_sales

        total_cost = ingredient_cost + fixed_cost_share + expense_share

        calc = CostCalculation.objects.create(
            product=product,
            expected_monthly_sales=expected_sales,
            ingredient_cost=ingredient_cost,
            fixed_cost_share=fixed_cost_share,
            expense_share=expense_share,
            total_cost=total_cost,
        )

        return Response(
            CostCalculationSerializer(calc).data,
            status=status.HTTP_201_CREATED
        )