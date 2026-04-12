from django.urls import path
from . import views

app_name = 'calculations'

urlpatterns = [
    path('calculos/',             views.calculation_list, name='list'),
    path('previsao/',             views.forecast_list,    name='forecast_list'),
    path('previsao/nova/',        views.forecast_new,     name='forecast_new'),
    path('ggf/',                  views.ggf_dashboard,    name='ggf'),
]