from django.urls import path
from . import views

app_name = 'calculations'

urlpatterns = [
    path('calculos/',      views.calculation_list, name='list'),
    path('calculos/novo/', views.calculation_new,  name='new'),
]
