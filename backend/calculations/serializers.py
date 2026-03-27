from rest_framework import serializers
from .models import FixedCost, Expense, CostCalculation


class FixedCostSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FixedCost
        fields = ('id', 'name', 'category', 'monthly_amount', 'is_active')
        read_only_fields = ('id',)


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Expense
        fields = ('id', 'name', 'amount', 'date', 'note')
        read_only_fields = ('id',)


class CostCalculationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model  = CostCalculation
        fields = (
            'id', 'product', 'product_name',
            'expected_monthly_sales',
            'ingredient_cost', 'fixed_cost_share',
            'expense_share',   'total_cost',
            'created_at'
        )
        # todos os campos de custo são gerados pelo sistema
        read_only_fields = (
            'id', 'ingredient_cost', 'fixed_cost_share',
            'expense_share', 'total_cost', 'created_at'
        )
''