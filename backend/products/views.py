from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.mixins import AuthMixin
from .models import Product, RecipeItem
from ingredients.models import Ingredient


class ProductListView(AuthMixin, View):
    template_name = 'products/list.html'

    def get(self, request):
        products = Product.objects.filter(
            is_active=True
        ).prefetch_related('recipe_items__ingredient')
        return render(request, self.template_name, {'products': products})


class ProductCreateView(AuthMixin, View):
    template_name = 'products/form.html'

    def get(self, request):
        ingredients = Ingredient.objects.filter(
            is_active=True
        ).order_by('name')
        return render(request, self.template_name, {
            'ingredients': ingredients,
            'action':      'create',
        })

    def post(self, request):
        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        sale_price  = request.POST.get('sale_price', 0)

        if not name:
            messages.error(request, 'Nome do produto é obrigatório.')
            return redirect('products:create')

        ingredient_ids = request.POST.getlist('ingredient_id[]')
        quantities     = request.POST.getlist('quantity[]')

        items = [
            (iid, qty)
            for iid, qty in zip(ingredient_ids, quantities)
            if iid and qty
        ]

        if not items:
            messages.error(request, 'Adicione ao menos um ingrediente à receita.')
            return redirect('products:create')

        try:
            product = Product.objects.create(
                name=name,
                description=description,
                sale_price=sale_price,
            )
            for ingredient_id, quantity in items:
                RecipeItem.objects.create(
                    product=product,
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                )
            messages.success(request, f'Produto "{name}" criado com sucesso!')
            return redirect('products:list')
        except Exception as e:
            messages.error(request, f'Erro ao criar produto: {e}')
            return redirect('products:create')


class ProductEditView(AuthMixin, View):
    template_name = 'products/form.html'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, owner=request.user)
        ingredients = Ingredient.objects.filter(
            is_active=True
        ).order_by('name')
        return render(request, self.template_name, {
            'product':     product,
            'ingredients': ingredients,
            'action':      'edit',
        })

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, owner=request.user)

        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        sale_price  = request.POST.get('sale_price', 0)

        if not name:
            messages.error(request, 'Nome do produto é obrigatório.')
            return redirect('products:edit', pk=pk)

        ingredient_ids = request.POST.getlist('ingredient_id[]')
        quantities     = request.POST.getlist('quantity[]')

        items = [
            (iid, qty)
            for iid, qty in zip(ingredient_ids, quantities)
            if iid and qty
        ]

        if not items:
            messages.error(request, 'Adicione ao menos um ingrediente.')
            return redirect('products:edit', pk=pk)

        try:
            # atualiza cabeçalho
            product.name        = name
            product.description = description
            product.sale_price  = sale_price
            product.save()

            # recria os itens da receita
            product.recipe_items.all().delete()
            for ingredient_id, quantity in items:
                RecipeItem.objects.create(
                    product=product,
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                )
            messages.success(request, f'Produto "{name}" atualizado!')
            return redirect('products:list')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {e}')
            return redirect('products:edit', pk=pk)


class ProductToggleView(AuthMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.is_active = not product.is_active
        product.save()
        status = 'ativado' if product.is_active else 'desativado'
        messages.success(request, f'Produto {status}.')
        return redirect('products:list')