from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import CartForm, CustomerForm
from .models import Cart, Product, Customer


def home_view(request):
    return render(request, 'home.html')


def product_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'product_detail.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            cart, created = Cart.objects.get_or_create(customer=request.user.customer)
            cart.product = product
            cart.quantity = quantity
            cart.save()
            return redirect('cart')
            # Перенаправление на страницу корзины после добавления товара
    else:
        form = CartForm()
    return render(request, 'add_to_cart.html', {'form': form})


def create_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
            # Перенаправление на список клиентов после создания
    else:
        form = CustomerForm()
    return render(request, 'create_customer.html', {'form': form})


def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
            # Перенаправление на список клиентов после редактирования
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
