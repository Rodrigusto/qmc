from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
from ingredients.models import Ingredient
from core.utils import to_decimal


class Product(BaseModel):
    name = models.CharField("Nome", max_length=100)
    description = models.TextField("Descrição", blank=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def ingredient_cost(self):
        """Soma o custo de todos os ingredientes da receita."""
        return sum(item.total_cost for item in self.recipe_items.all())


class RecipeItem(BaseModel):
    """
    Tabela intermediária: qual ingrediente, em qual quantidade,
    para qual produto. Ex: X-Burger usa 40g de maionese.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="recipe_items"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,  # não deixa apagar ingrediente em uso
        related_name="recipe_items",
    )
    quantity = models.DecimalField(
        "Quantidade",
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
    )
    sale_price = models.DecimalField(
        "Preço de venda (R$)", max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = "Item do Produto"
        verbose_name_plural = "Itens do Produto"
        unique_together = ("product", "ingredient")  # sem duplicatas

    def __str__(self):
        return f"{self.quantity}{self.ingredient.unit} de {self.ingredient.name}"

    @property
    def total_cost(self):
        """Custo deste ingrediente nesta receita."""
        self.quantity = to_decimal(self.quantity)
        self.ingredient.cost_per_unit = to_decimal(self.ingredient.cost_per_unit)
        return self.quantity * self.ingredient.cost_per_unit
