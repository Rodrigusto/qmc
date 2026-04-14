from django.contrib import admin
from .models import Neighborhood, SalesChannel, Customer, Sale, SaleItem


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display  = ('name', 'delivery_fee', 'is_active')
    list_editable = ('delivery_fee', 'is_active')
    search_fields = ('name',)


@admin.register(SalesChannel)
class SalesChannelAdmin(admin.ModelAdmin):
    list_display  = ('name', 'fee_type', 'fee_value', 'is_active')
    list_editable = ('is_active',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ('name', 'phone', 'is_active')
    search_fields = ('name', 'phone')
    list_editable = ('is_active',)


class SaleItemInline(admin.TabularInline):
    model           = SaleItem
    extra           = 2
    fields          = ('product', 'quantity', 'unit_price', 'subtotal_display')
    readonly_fields = ('subtotal_display',)

    def subtotal_display(self, obj):
        if obj.pk:
            return f'R$ {obj.subtotal:.2f}'
        return '—'
    subtotal_display.short_description = 'Subtotal'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display  = ('date', 'customer', 'channel', 'status', 'subtotal', 'total')
    list_filter   = ('status', 'channel', 'date')
    search_fields = ('customer__name',)
    date_hierarchy = 'date'
    inlines       = (SaleItemInline,)
    readonly_fields = ('subtotal', 'channel_fee', 'delivery_fee', 'total')