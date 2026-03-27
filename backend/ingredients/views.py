from django.shortcuts import render, get_object_or_404
from .models import Ingredient


def ingredient_list(request):
    ingredients = Ingredient.objects.filter(is_active=True)
    return render(request, 'ingredients/list.html', {'ingredients': ingredients})


def ingredient_detail(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    return render(request, 'ingredients/detail.html', {'ingredient': ingredient})

