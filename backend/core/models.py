import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Model base herdado por todos os outros.
    Fornece id único, datas de criação/atualização
    e soft delete (desativar sem apagar do banco).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True  # não gera tabela, só serve de base
