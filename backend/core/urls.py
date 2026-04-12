from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # rotas web — HTML
    path('', include('products.urls')),
    path('', include('calculations.urls')),
    path('', include('purchases.urls')),

    # rotas API — JSON para o Flet
    path('api/', include('api.urls')),
]
