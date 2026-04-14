from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('vendas/',              views.sale_list,         name='list'),
    path('vendas/nova/',         views.sale_new,          name='new'),
    path('vendas/resumo/',       views.sale_summary,      name='summary'),
    path('vendas/<uuid:pk>/cancelar/', views.sale_cancel, name='cancel'),
    path('clientes/',            views.customer_list,     name='customers'),
    path('bairros/',             views.neighborhood_list, name='neighborhoods'),
    path('canais/',              views.channel_list,      name='channels'),
]