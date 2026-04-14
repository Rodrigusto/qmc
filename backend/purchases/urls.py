from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('compras/',        views.purchase_list,   name='list'),
    path('compras/nova/',   views.purchase_new,    name='new'),
    path('estoque/',        views.stock_list,       name='stock'),
    path('compras/<uuid:pk>/cancelar/', views.purchase_cancel, name='cancel'),
    path('fornecedores/', views.supplier_list, name='suppliers'),
]