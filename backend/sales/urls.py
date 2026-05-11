from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path("vendas/", views.SaleListView.as_view(), name="list"),
    path("vendas/nova/", views.SaleCreateView.as_view(), name="new"),
    path("vendas/resumo/", views.SaleSummaryView.as_view(), name="summary"),
    path("vendas/<uuid:pk>/cancelar/", views.SaleCancelView.as_view(), name="cancel"),
    path("clientes/", views.CustomerListView.as_view(), name="customers"),
    path("bairros/", views.NeighborhoodListView.as_view(), name="neighborhoods"),
    path("canais/", views.ChannelListView.as_view(), name="channels"),
]
