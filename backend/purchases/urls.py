from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('compras/',        views.purchase_list,   name='list'),
    path('compras/nova/',   views.purchase_new,    name='new'),
    path('estoque/',        views.stock_list,       name='stock'),
]