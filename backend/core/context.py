from .menu import get_menu


def base_context(request):
    return {
        "menu": get_menu(),
        "app_name": request.resolver_match.app_name,
        "url_name": request.resolver_match.url_name,
    }
