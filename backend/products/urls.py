from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('produtos/',          views.product_list,   name='list'),
    path('produtos/<uuid:pk>/',views.product_detail, name='detail'),
]
