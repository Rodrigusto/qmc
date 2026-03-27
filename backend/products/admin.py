from django.contrib import admin
from .models import Product, RecipeItem


class RecipeItemInline(admin.TabularInline):
    """
    Exibe os ingredientes da receita diretamente
    na página do produto. Muito mais prático.
    """
    model       = RecipeItem
    extra       = 3          # 3 linhas vazias para adicionar
    min_num     = 1          # obriga ao menos 1 ingrediente
    fields      = ('ingredient', 'quantity', 'total_cost_display')
    readonly_fields = ('total_cost_display',)

    def total_cost_display(self, obj):
        if obj.pk:
            return f'R$ {obj.total_cost:.4f}'
        return '—'
    total_cost_display.short_description = 'Custo'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'ingredient_cost_display', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('name',)
    inlines       = (RecipeItemInline,)
    readonly_fields = ('ingredient_cost_display',)

    def ingredient_cost_display(self, obj):
        return f'R$ {obj.ingredient_cost:.2f}'
    ingredient_cost_display.short_description = 'Custo ingredientes'
