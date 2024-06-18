from django.shortcuts import render, redirect
from .forms import CartForm
from .models import Cart
from .models import Product


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def add_to_cart(request):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            Cart.objects.create(customer=request.user.customer, product=product, quantity=quantity)
            return redirect('product_list')
    else:
        form = CartForm()
    return render(request, 'add_to_cart.html', {'form': form})

