from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next", "/"))
        messages.error(request, "Usuário ou senha incorretos.")
    return render(request, "users/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("/login/")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        # validações
        if not username or not password1:
            messages.error(request, "Usuário e senha são obrigatórios.")
        elif password1 != password2:
            messages.error(request, "As senhas não coincidem.")
        elif len(password1) < 6:
            messages.error(request, "A senha deve ter pelo menos 6 caracteres.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Este usuário já está em uso.")
        elif email and User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                password=password1,
                is_staff=False,  # sem acesso ao admin
                is_superuser=False,
            )
            login(request, user)
            messages.success(request, f"Bem-vindo, {first_name or username}!")
            return redirect("/")

    return render(request, "users/register.html")
