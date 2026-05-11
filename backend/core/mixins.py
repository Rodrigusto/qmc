from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from api.menu import menu_view


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resolver = self.request.resolver_match

        context["menu"] = menu_view()
        context["url_name"] = resolver.url_name
        context["app_name"] = resolver.app_name

        return context


class AuthMixin(LoginRequiredMixin):
    """
    Herdar em todas as CBVs do projeto.
    Redireciona para login se não autenticado.
    """

    login_url = "/login/"


def auth_required(view_func):
    """Decorator para FBVs."""
    return login_required(view_func, login_url="/login/")
