from django.shortcuts import render, get_object_or_404
from .models import Ingredient
from core.context import base_context
from core.mixins import auth_required

@auth_required
def ingredient_list(request):
    ingredients = Ingredient.objects.filter(is_active=True)
    context = {
        "ingredients": ingredients,
        **base_context(request),
    }
    return render(request, "ingredients/list.html", context)


@auth_required
def ingredient_detail(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    context = {
        "ingredient": ingredient,
        **base_context(request),
    }
    return render(request, "ingredients/detail.html", context)
