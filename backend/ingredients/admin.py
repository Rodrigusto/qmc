from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display  = ('name', 'unit', 'cost_per_unit', 'is_active')
    list_filter   = ('unit', 'is_active')
    search_fields = ('name',)
    ordering      = ('name',)
    
    # editar is_active direto na listagem, sem abrir o registro
    list_editable = ('is_active',)
