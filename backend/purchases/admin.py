from django.contrib import admin
from .models import Supplier, Purchase, PurchaseItem, Stock


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display  = ('name', 'phone', 'email', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active',)


class PurchaseItemInline(admin.TabularInline):
    model           = PurchaseItem
    extra           = 3
    fields          = ('ingredient', 'quantity', 'total_price', 'unit_price_display')
    readonly_fields = ('unit_price_display',)

    def unit_price_display(self, obj):
        if obj.pk:
            return f'R$ {obj.unit_price:.4f} / {obj.ingredient.unit}'
        return '—'
    unit_price_display.short_description = 'Custo unitário'


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display    = ('supplier', 'date', 'total_amount_display')
    list_filter     = ('supplier', 'date')
    search_fields   = ('supplier__name',)
    date_hierarchy  = 'date'
    inlines         = (PurchaseItemInline,)
    readonly_fields = ('total_amount_display',)

    def total_amount_display(self, obj):
        return f'R$ {obj.total_amount:.2f}'
    total_amount_display.short_description = 'Total da compra'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display    = ('ingredient', 'quantity_display', 'current_value_display', 'status')
    search_fields   = ('ingredient__name',)
    readonly_fields = ('ingredient', 'quantity', 'current_value_display')

    def quantity_display(self, obj):
        return f'{obj.quantity} {obj.ingredient.unit}'
    quantity_display.short_description = 'Saldo'

    def current_value_display(self, obj):
        return f'R$ {obj.current_value:.2f}'
    current_value_display.short_description = 'Valor em estoque'

    def status(self, obj):
        if obj.is_low:
            return '⚠ Estoque baixo'
        return '✓ Ok'
    status.short_description = 'Status'

    def has_add_permission(self, request):
        return False  # estoque só é criado via compra