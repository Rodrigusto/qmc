from django.http import JsonResponse
from core.menu import get_menu


def menu_view(request):
    return JsonResponse(get_menu(), safe=False)


"""
from django.http import JsonResponse
from .menu import get_menu

def menu_view(request):
    menu = get_menu(request.user)
    return JsonResponse(menu, safe=False)
"""
