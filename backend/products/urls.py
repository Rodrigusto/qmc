from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('produtos/',                    views.ProductListView.as_view(),   name='list'),
    path('produtos/novo/',               views.ProductCreateView.as_view(), name='create'),
    path('produtos/<uuid:pk>/editar/',   views.ProductEditView.as_view(),   name='edit'),
    path('produtos/<uuid:pk>/toggle/',   views.ProductToggleView.as_view(), name='toggle'),
]