from django.urls import path
from . import views

app_name = "purchases"

urlpatterns = [
    path("compras/", views.PurchaseListView.as_view(), name="list"),
    path("compras/nova/", views.PurchaseCreateView.as_view(), name="new"),
    path(
        "compras/<uuid:pk>/cancelar/", views.PurchaseCancelView.as_view(), name="cancel"
    ),
    path("estoque/", views.StockListView.as_view(), name="stock"),
    path("fornecedores/", views.SupplierListView.as_view(), name="suppliers"),
]
