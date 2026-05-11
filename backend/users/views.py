from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    # já logado → vai para home
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # redireciona para página que tentou acessar, ou home
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "users/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("/login/")
