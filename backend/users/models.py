
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    User customizado. Mesmo que vazio agora,
    garante flexibilidade futura sem resetar o banco.
    """
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

