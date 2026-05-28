from django.urls import path
from . import views

app_name = "calculations"

urlpatterns = [
    path("calculos/",                views.calculation_list, name="list"),
    path("previsao/",                views.forecast_list, name="forecast_list"),
    path("previsao/nova/",           views.forecast_new, name="forecast_new"),
    path("ggf/",                     views.ggf_dashboard, name="ggf"),
    path('custos-fixos/',                      views.FixedCostListView.as_view(),  name='fixed_costs'),
    path('custos-fixos/<uuid:pk>/deletar/',    views.FixedCostDeleteView.as_view(), name='fixed_cost_delete'),
    path('despesas/',                          views.ExpenseListView.as_view(),     name='expenses'),
    path('despesas/<uuid:pk>/deletar/',        views.ExpenseDeleteView.as_view(),   name='expense_delete'),
]
