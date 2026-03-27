from rest_framework import serializers
from .models import Product, RecipeItem
from ingredients.serializers import IngredientSerializer


class RecipeItemSerializer(serializers.ModelSerializer):
    # campo calculado — só leitura, não vem do banco direto
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=4,
        read_only=True
    )

    class Meta:
        model  = RecipeItem
        fields = ('id', 'ingredient', 'quantity', 'total_cost')


class ProductSerializer(serializers.ModelSerializer):
    # aninha os itens da receita dentro do produto
    recipe_items    = RecipeItemSerializer(many=True, read_only=True)
    ingredient_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        read_only=True
    )

    class Meta:
        model  = Product
        fields = ('id', 'name', 'description', 'recipe_items', 'ingredient_cost')
