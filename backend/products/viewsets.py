from rest_framework import viewsets, filters
from .models import Product
from .serializers import ProductSerializer
from core.mixins import LoginRequiredMixin


class ProductViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related(
            "recipe_items__ingredient"
        )
