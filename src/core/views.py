import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CartForm, CustomerForm, CustomerRegistrationForm
from .models import Cart, Product, Customer

env_logger = logging.getLogger('env_logger')


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


@login_required
def add_to_cart(request):
    env_logger.debug("Entered add_to_cart view")

    if request.method == 'POST':
        env_logger.debug("Request method is POST")

        form = CartForm(request.POST)
        if form.is_valid():
            env_logger.debug("Form is valid")

            user_email = request.user.email  # используем email текущего пользователя
            try:
                customer = Customer.objects.get(email=user_email)  # получаем объект Customer по email
            except Customer.DoesNotExist:
                env_logger.error(f"Customer with email {user_email} does not exist")
                return HttpResponse("Customer not found", status=404)

            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            env_logger.debug(f"Customer: {customer}, Product: {product}, Quantity: {quantity}")

            cart_item, created = Cart.objects.get_or_create(
                customer=customer,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            env_logger.debug(f"Cart item created: {created}, Quantity after update: {cart_item.quantity}")

            return redirect('add_to_cart')  # замените на ваш URL успешного добавления
        else:
            env_logger.error("Form is not valid")
            env_logger.debug(form.errors)
    else:
        env_logger.debug("Request method is not POST")
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
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, email=customer.email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register.html', {'form': form})
