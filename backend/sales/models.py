from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import BaseModel
from products.models import Product
from purchases.models import Stock


class Neighborhood(BaseModel):
    """Bairro com taxa de entrega própria."""
    name          = models.CharField('Nome', max_length=100)
    delivery_fee  = models.DecimalField(
        'Taxa de entrega (R$)',
        max_digits=8,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name        = 'Bairro'
        verbose_name_plural = 'Bairros'
        ordering            = ['name']

    def __str__(self):
        return f'{self.name} — R$ {self.delivery_fee}'


class SalesChannel(BaseModel):
    """
    Canal de venda — balcão, delivery próprio, iFood, Uber Eats, etc.
    A taxa pode ser percentual (iFood 30%) ou fixa (R$ 5,00 por pedido).
    """
    class FeeType(models.TextChoices):
        PERCENT = 'percent', 'Percentual (%)'
        FIXED   = 'fixed',   'Valor fixo (R$)'
        NONE    = 'none',    'Sem taxa'

    name     = models.CharField('Nome', max_length=100)
    fee_type = models.CharField(
        'Tipo de taxa',
        max_length=10,
        choices=FeeType.choices,
        default=FeeType.NONE
    )
    fee_value = models.DecimalField(
        'Valor da taxa',
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text='% se percentual, R$ se fixo'
    )

    class Meta:
        verbose_name        = 'Canal de venda'
        verbose_name_plural = 'Canais de venda'
        ordering            = ['name']

    def __str__(self):
        return self.name

    def calculate_fee(self, subtotal: Decimal) -> Decimal:
        """Calcula a taxa do canal sobre o subtotal da venda."""
        if self.fee_type == self.FeeType.PERCENT:
            return subtotal * (Decimal(str(self.fee_value)) / 100)
        elif self.fee_type == self.FeeType.FIXED:
            return Decimal(str(self.fee_value))
        return Decimal('0')


class Customer(BaseModel):
    """Cliente — vinculado às vendas para histórico."""
    name  = models.CharField('Nome', max_length=100)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    note  = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name        = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering            = ['name']

    def __str__(self):
        return self.name


class Sale(BaseModel):
    """
    Cabeçalho da venda.
    Ao salvar, deduz automaticamente os ingredientes do estoque.
    """
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pendente'
        CONFIRMED = 'confirmed', 'Confirmado'
        DELIVERED = 'delivered', 'Entregue'
        CANCELLED = 'cancelled', 'Cancelado'

    date          = models.DateField('Data')
    channel       = models.ForeignKey(
        SalesChannel,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Canal'
    )
    customer      = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Cliente',
        null=True, blank=True
    )
    neighborhood  = models.ForeignKey(
        Neighborhood,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Bairro',
        null=True, blank=True
    )
    status        = models.CharField(
        'Status',
        max_length=12,
        choices=Status.choices,
        default=Status.CONFIRMED
    )
    discount      = models.DecimalField(
        'Desconto (R$)',
        max_digits=8,
        decimal_places=2,
        default=0
    )
    note          = models.TextField('Observações', blank=True)

    # campos calculados — preenchidos no save()
    subtotal      = models.DecimalField(
        'Subtotal', max_digits=10, decimal_places=2, default=0
    )
    channel_fee   = models.DecimalField(
        'Taxa do canal', max_digits=10, decimal_places=2, default=0
    )
    delivery_fee  = models.DecimalField(
        'Taxa de entrega', max_digits=10, decimal_places=2, default=0
    )
    total         = models.DecimalField(
        'Total', max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name        = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering            = ['-date', '-created_at']

    def __str__(self):
        return f'Venda #{str(self.pk)[:8]} — {self.date} — R$ {self.total}'

    def recalculate_totals(self):
        """Recalcula subtotal, taxas e total da venda."""
        self.subtotal = sum(
            item.subtotal for item in self.items.all()
        )
        self.channel_fee  = self.channel.calculate_fee(self.subtotal)
        self.delivery_fee = Decimal(str(self.neighborhood.delivery_fee)) if self.neighborhood else Decimal('0')
        self.discount     = Decimal(str(self.discount))
        self.total        = self.subtotal + self.delivery_fee - self.discount

    def deduct_stock(self):
        """
        Deduz os ingredientes de cada item da receita do estoque.
        Chamado uma única vez na confirmação da venda.
        """
        for item in self.items.all():
            for recipe_item in item.product.recipe_items.all():
                needed = recipe_item.quantity * item.quantity
                try:
                    stock = Stock.objects.get(ingredient=recipe_item.ingredient)
                    stock.quantity = max(Decimal('0'), stock.quantity - needed)
                    stock.save()
                except Stock.DoesNotExist:
                    pass  # ingrediente sem estoque registrado — ignora


class SaleItem(BaseModel):
    """Item da venda — produto, quantidade e preço no momento da venda."""
    sale      = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Venda'
    )
    product   = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sale_items',
        verbose_name='Produto'
    )
    quantity  = models.PositiveIntegerField(
        'Quantidade',
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        'Preço unitário (R$)',
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name        = 'Item da venda'
        verbose_name_plural = 'Itens da venda'

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'

    @property
    def subtotal(self):
        return Decimal(str(self.unit_price)) * self.quantity