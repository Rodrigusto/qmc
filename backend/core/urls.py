from django.contrib import admin
from django.urls import path, include
from core.views import DashboardView

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('',          DashboardView.as_view(),    name='dashboard'),
    path('',          include('users.urls')),
    path('',          include('ingredients.urls')),
    path('',          include('products.urls')),
    path('',          include('purchases.urls')),
    path('',          include('calculations.urls')),
    path('',          include('sales.urls')),
    path('api/',      include('api.urls')),
]