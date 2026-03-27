from django.urls import path
from . import views

app_name = 'ingredients'

urlpatterns = [
    path('ingredientes/',          views.ingredient_list,   name='list'),
    path('ingredientes/<uuid:pk>/',views.ingredient_detail, name='detail'),
]
