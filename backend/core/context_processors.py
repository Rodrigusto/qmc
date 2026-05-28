from core.menu import get_menu


def menu(request):
    """
    Injeta o menu em todos os templates automaticamente.
    """
    return {"menu": get_menu()}
