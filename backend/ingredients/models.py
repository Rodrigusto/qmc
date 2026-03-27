from django.db import models
from core.models import BaseModel


class Ingredient(BaseModel):
    
    class Unit(models.TextChoices):
        GRAM     = 'g',  'Grama'
        KILOGRAM = 'kg', 'Quilograma'
        UNIT     = 'un', 'Unidade'
        LITER    = 'l',  'Litro'
        MILILITER = 'ml', 'Mililitro'

    name = models.CharField('Nome', max_length=100)
    unit = models.CharField(
        'Unidade',
        max_length=5,
        choices=Unit.choices,
        default=Unit.GRAM
    )
    cost_per_unit = models.DecimalField(
        'Custo por unidade',
        max_digits=10,
        decimal_places=4  # 4 casas: ex. R$ 0,0153 por grama
    )

    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.unit})'
