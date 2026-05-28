from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import Tenant, Domain
from users.models import User
import re


def landing(request):
    """Página pública — apresenta o produto."""
    return render(request, 'tenants/landing.html')


def register_tenant(request):
    """
    Cadastro de novo cliente.
    Cria o tenant, o schema, o domínio e o usuário admin.
    """
    if request.method == 'POST':
        business_name = request.POST.get('business_name', '').strip()
        subdomain     = request.POST.get('subdomain', '').strip().lower()
        first_name    = request.POST.get('first_name', '').strip()
        username      = request.POST.get('username', '').strip()
        email         = request.POST.get('email', '').strip()
        password1     = request.POST.get('password1', '')
        password2     = request.POST.get('password2', '')

        # validações
        errors = []

        if not business_name:
            errors.append('Nome do negócio é obrigatório.')

        if not subdomain:
            errors.append('Subdomínio é obrigatório.')
        elif not re.match(r'^[a-z0-9-]+$', subdomain):
            errors.append('Subdomínio só pode ter letras minúsculas, números e hífens.')
        elif Domain.objects.filter(domain__startswith=subdomain + '.').exists():
            errors.append('Este subdomínio já está em uso.')

        if not username:
            errors.append('Usuário é obrigatório.')

        if password1 != password2:
            errors.append('As senhas não coincidem.')

        if len(password1) < 6:
            errors.append('A senha deve ter pelo menos 6 caracteres.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'tenants/register.html',
                          {'post': request.POST})

        try:
            # 1. cria o tenant (cria o schema automaticamente)
            tenant = Tenant(
                schema_name=subdomain,
                name=business_name,
            )
            tenant.save()

            # 2. vincula o domínio
            host = request.get_host().split(':')[0]  # remove a porta
            domain_url = f'{subdomain}.{host}'
            Domain.objects.create(
                domain=domain_url,
                tenant=tenant,
                is_primary=True,
            )

            # 3. cria o usuário admin dentro do schema do tenant
            from django_tenants.utils import tenant_context
            with tenant_context(tenant):
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    password=password1,
                    is_staff=True,
                )

            messages.success(
                request,
                f'Conta criada! Acesse: {domain_url}'
            )
            return redirect(f'http://{domain_url}/login/')

        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {e}')

    return render(request, 'tenants/register.html')