from django.shortcuts import render, get_object_or_404
from .models import Product
from core.context import base_context
from core.mixins import auth_required

@auth_required
def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related(
        "recipe_items__ingredient"
    )
    context = {
        "products": products,
        **base_context(request),
    }
    return render(request, "products/list.html", context)


@auth_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    context = {
        "product": product,
        **base_context(request),
    }
    return render(request, "products/detail.html", context)
