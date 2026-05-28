from django.urls import path
from . import views

app_name = 'ingredients'

urlpatterns = [
    path('ingredientes/', views.IngredientListView.as_view(), name='list'),
]