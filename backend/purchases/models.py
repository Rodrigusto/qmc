# purchases/models.py — versão limpa

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import BaseModel
from ingredients.models import Ingredient


class Supplier(BaseModel):
    name  = models.CharField('Nome', max_length=100)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    note  = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name        = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering            = ['name']

    def __str__(self):
        return self.name


class Purchase(BaseModel):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT,
        related_name='purchases', verbose_name='Fornecedor'
    )
    date = models.DateField('Data da compra')
    note = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name        = 'Compra'
        verbose_name_plural = 'Compras'
        ordering            = ['-date']

    def __str__(self):
        return f'Compra {self.supplier.name} — {self.date}'

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class PurchaseItem(BaseModel):
    purchase   = models.ForeignKey(
        Purchase, on_delete=models.CASCADE,
        related_name='items', verbose_name='Compra'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT,
        related_name='purchase_items', verbose_name='Ingrediente'
    )
    quantity    = models.DecimalField(
        'Quantidade', max_digits=10, decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    total_price = models.DecimalField(
        'Valor total pago (R$)', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        verbose_name        = 'Item da compra'
        verbose_name_plural = 'Itens da compra'

    def __str__(self):
        return f'{self.quantity} {self.ingredient.unit} de {self.ingredient.name}'

    @property
    def unit_price(self):
        quantity    = Decimal(str(self.quantity))
        total_price = Decimal(str(self.total_price))
        return total_price / quantity if quantity > 0 else Decimal('0')


class Stock(BaseModel):
    ingredient = models.OneToOneField(
        Ingredient, on_delete=models.PROTECT,
        related_name='stock', verbose_name='Ingrediente'
    )
    quantity = models.DecimalField(
        'Quantidade em estoque', max_digits=10,
        decimal_places=3, default=0
    )

    class Meta:
        verbose_name        = 'Estoque'
        verbose_name_plural = 'Estoque'
        ordering            = ['ingredient__name']

    def __str__(self):
        return f'{self.ingredient.name}: {self.quantity} {self.ingredient.unit}'

    @property
    def is_low(self):
        return self.quantity < 10

    @property
    def current_value(self):
        return Decimal(str(self.quantity)) * Decimal(str(self.ingredient.cost_per_unit))