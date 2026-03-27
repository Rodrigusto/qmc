from rest_framework import viewsets, filters
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset         = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['name']
    ordering_fields  = ['name', 'cost_per_unit']
    ordering         = ['name']

    def get_queryset(self):
        if self.request.query_params.get('all'):
            return Ingredient.objects.all()
        return Ingredient.objects.filter(is_active=True)