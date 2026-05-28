from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Tenant(TenantMixin):
    """
    Representa cada cliente do sistema.
    Cada tenant tem seu próprio schema no PostgreSQL.
    """
    name       = models.CharField('Nome do negócio', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)

    # django-tenants cria o schema automaticamente ao salvar
    auto_create_schema = True

    class Meta:
        verbose_name        = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """
    Domínio/subdomínio vinculado ao tenant.
    Ex: burguerx.seuapp.com → schema burguerx
    Um tenant pode ter múltiplos domínios.
    """
    class Meta:
        verbose_name        = 'Domínio'
        verbose_name_plural = 'Domínios'