from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
from products.models import Product


class FixedCost(BaseModel):
    """Custos fixos mensais: aluguel, luz, salários..."""
    
    class Category(models.TextChoices):
        RENT     = 'rent',    'Aluguel'
        SALARY   = 'salary',  'Salários'
        UTILITY  = 'utility', 'Utilidades (água/luz)'
        OTHER    = 'other',   'Outros'

    name = models.CharField('Nome', max_length=100)
    category = models.CharField(
        'Categoria',
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )
    monthly_amount = models.DecimalField(
        'Valor mensal (R$)',
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Custo fixo'
        verbose_name_plural = 'Custos fixos'

    def __str__(self):
        return f'{self.name}: R$ {self.monthly_amount}'


class Expense(BaseModel):
    """Despesas variáveis: conserto de geladeira, gasolina..."""
    name = models.CharField('Nome', max_length=100)
    amount = models.DecimalField(
        'Valor (R$)',
        max_digits=10,
        decimal_places=2
    )
    date = models.DateField('Data')
    note = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-date']

    def __str__(self):
        return f'{self.name}: R$ {self.amount}'


class CostCalculation(BaseModel):
    """
    Snapshot do cálculo de custo de um produto.
    Registra o resultado no momento do cálculo — 
    histórico preservado mesmo se custos mudarem depois.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='calculations'
    )
    expected_monthly_sales = models.PositiveIntegerField(
        'Vendas mensais esperadas',
        validators=[MinValueValidator(1)]
    )
    # valores salvos no momento do cálculo
    ingredient_cost  = models.DecimalField(max_digits=10, decimal_places=4)
    fixed_cost_share = models.DecimalField(max_digits=10, decimal_places=4)
    expense_share    = models.DecimalField(max_digits=10, decimal_places=4)
    total_cost       = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        verbose_name = 'Cálculo de custo'
        verbose_name_plural = 'Cálculos de custo'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} — R$ {self.total_cost}'
