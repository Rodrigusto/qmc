from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
from ingredients.models import Ingredient
from decimal import Decimal

class Supplier(BaseModel):
    """Fornecedor — de quem você compra."""
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
    """
    Cabeçalho da compra.
    Uma compra pode ter vários itens (PurchaseItem).
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchases',
        verbose_name='Fornecedor'
    )
    date     = models.DateField('Data da compra')
    note     = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name        = 'Compra'
        verbose_name_plural = 'Compras'
        ordering            = ['-date']

    def __str__(self):
        return f'Compra {self.supplier.name} — {self.date}'

    @property
    def total_amount(self):
        """Soma o valor total de todos os itens da compra."""
        return sum(item.total_price for item in self.items.all())


class PurchaseItem(BaseModel):
    """
    Item da compra — sempre na unidade base do ingrediente.
    Ex: 100 unidades de pão por R$ 100,00 → R$ 1,00/un
        500 gramas de batata palha por R$ 15,00 → R$ 0,03/g
    Ao salvar, atualiza o custo médio ponderado do ingrediente
    e o saldo do estoque automaticamente.
    """
    purchase   = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Compra'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='purchase_items',
        verbose_name='Ingrediente'
    )
    quantity    = models.DecimalField(
        'Quantidade',
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001)]
    )
    total_price = models.DecimalField(
        'Valor total pago (R$)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
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
        if quantity > 0:
            return total_price / quantity
        return Decimal('0')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_stock_and_cost()


    def _update_stock_and_cost(self):
        stock, _ = Stock.objects.get_or_create(ingredient=self.ingredient)

        saldo_atual  = Decimal(str(stock.quantity))
        custo_atual  = Decimal(str(self.ingredient.cost_per_unit))
        qtd_nova     = Decimal(str(self.quantity))
        custo_novo   = self.unit_price

        novo_saldo = saldo_atual + qtd_nova

        if novo_saldo > 0:
            novo_custo_medio = (
                (saldo_atual * custo_atual) + (qtd_nova * custo_novo)
            ) / novo_saldo
        else:
            novo_custo_medio = custo_novo

        stock.quantity = novo_saldo
        stock.save()

        self.ingredient.cost_per_unit = novo_custo_medio
        self.ingredient.save()


class Stock(BaseModel):
    """
    Saldo atual de cada ingrediente.
    Uma linha por ingrediente — atualizada a cada compra (e futuramente a cada venda).
    """
    ingredient = models.OneToOneField(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='stock',
        verbose_name='Ingrediente'
    )
    quantity   = models.DecimalField(
        'Quantidade em estoque',
        max_digits=10,
        decimal_places=3,
        default=0
    )

    class Meta:
        verbose_name        = 'Estoque'
        verbose_name_plural = 'Estoque'
        ordering            = ['ingredient__name']

    def __str__(self):
        return f'{self.ingredient.name}: {self.quantity} {self.ingredient.unit}'

    @property
    def is_low(self):
        """Saldo baixo — menos de 10 unidades/gramas."""
        return self.quantity < 10

    @property
    def current_value(self):
        """Valor total do estoque deste ingrediente."""
        return self.quantity * self.ingredient.cost_per_unit

