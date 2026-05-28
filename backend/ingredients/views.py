from django.views.generic import ListView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.mixins import AuthMixin
from .models import Ingredient


class IngredientListView(AuthMixin, View):
    template_name = 'ingredients/list.html'

    def get(self, request):
        ingredients = Ingredient.objects.filter(
            
        ).order_by('name')
        return render(request, self.template_name, {
            'ingredients': ingredients,
            'units': Ingredient.Unit.choices,
        })

    def post(self, request):
        action = request.POST.get('action')
        try:
            if action == 'create':
                Ingredient.objects.create(
                    name=request.POST['name'],
                    unit=request.POST['unit'],
                    cost_per_unit=request.POST.get('cost_per_unit', 0),
                )
                messages.success(request, 'Ingrediente cadastrado!')

            elif action == 'edit':
                ing = get_object_or_404(
                    Ingredient, pk=request.POST['pk'], 
                )
                ing.name          = request.POST['name']
                ing.unit          = request.POST['unit']
                ing.cost_per_unit = request.POST.get('cost_per_unit', 0)
                ing.save()
                messages.success(request, 'Ingrediente atualizado!')

            elif action == 'toggle':
                ing = get_object_or_404(
                    Ingredient, pk=request.POST['pk'], 
                )
                ing.is_active = not ing.is_active
                ing.save()
                messages.success(
                    request,
                    f'Ingrediente {"ativado" if ing.is_active else "desativado"}.'
                )
        except Exception as e:
            messages.error(request, f'Erro: {e}')

        return redirect('ingredients:list')