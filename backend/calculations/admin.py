from django.contrib import admin
from .models import FixedCost, Expense, CostCalculation


@admin.register(FixedCost)
class FixedCostAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'monthly_amount', 'is_active')
    list_filter   = ('category', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display  = ('name', 'amount', 'date')
    list_filter   = ('date',)
    search_fields = ('name',)
    date_hierarchy = 'date'    # navegação por período no topo da listagem
    ordering       = ('-date',)


@admin.register(CostCalculation)
class CostCalculationAdmin(admin.ModelAdmin):
    list_display  = (
        'product', 'expected_monthly_sales',
        'ingredient_cost', 'fixed_cost_share',
        'expense_share',   'total_cost',
        'created_at'
    )
    list_filter   = ('product',)
    search_fields = ('product__name',)
    readonly_fields = (
        'ingredient_cost', 'fixed_cost_share',
        'expense_share',   'total_cost',
        'created_at',      'updated_at'
    )
    # impede criação manual — cálculo será gerado pela view/service
    def has_add_permission(self, request):
        return False
