from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ingredients.viewsets import IngredientViewSet
from products.viewsets import ProductViewSet
from calculations.viewsets import (
    FixedCostViewSet,
    ExpenseViewSet,
    CostCalculationViewSet,
)
from .views import menu_view  # nova inclusao

router = DefaultRouter()
router.register("ingredients", IngredientViewSet)
router.register("products", ProductViewSet)
router.register("fixed-costs", FixedCostViewSet)
router.register("expenses", ExpenseViewSet)
router.register("calculations", CostCalculationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("menu/", menu_view),  # nova inclusao
    # path('grappelli/', include('grappelli.urls')), # grappeli urls
]
