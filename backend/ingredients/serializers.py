from rest_framework import serializers
from .models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ingredient
        fields = ('id', 'name', 'unit', 'cost_per_unit', 'is_active')
        read_only_fields = ('id',)
