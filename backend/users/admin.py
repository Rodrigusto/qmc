from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Herda tudo do UserAdmin padrão do Django.
    Pronto para customizar quando precisar.
    """
    pass
