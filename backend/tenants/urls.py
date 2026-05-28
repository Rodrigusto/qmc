from django.urls import path
from . import views

urlpatterns = [
    path('',          views.landing,        name='landing'),
    path('cadastro/', views.register_tenant, name='register_tenant'),
]