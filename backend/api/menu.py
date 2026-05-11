from django.http import JsonResponse
from core.menu import get_menu


def menu_view(request):
    return JsonResponse(get_menu(), safe=False)
