import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate


from .forms import CartForm, CustomerForm, CustomerRegistrationForm, OrderForm
from .models import Cart, Product, Customer, Order, CartItem, PurchaseHistory, Stock

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


@login_required
def place_order(request):
    env_logger.debug("Entered place_order view")

    if request.method == 'POST':
        env_logger.debug("Request method is POST")

        form = OrderForm(request.POST)
        form.fields['cart'].queryset = Cart.objects.filter(customer=request.user)
        if form.is_valid():
            env_logger.debug("Form is valid")

            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            delivery_datetime = form.cleaned_data['delivery_datetime']
            email = form.cleaned_data['email']
            cart = form.cleaned_data['cart']

            env_logger.debug(
                f"Name: {name}, Address: {address}, Email: {email}, Delivery Date and Time: {delivery_datetime}, Cart: {cart}")

            try:
                customer = Customer.objects.get(email=email)
                env_logger.debug(f"Customer found: {customer}")
            except Customer.DoesNotExist:
                env_logger.error(f"Customer with email {email} does not exist")
                return HttpResponse("Customer not found", status=404)

            try:
                # Проверка и обновление количества на складе для каждого элемента корзины
                cart_items = CartItem.objects.filter(cart=cart)
                for item in cart_items:
                    stock = Stock.objects.get(product=item.product)
                    if item.quantity > stock.quantity:
                        env_logger.error(f"Cannot order more than available stock: {stock.quantity}")
                        return HttpResponse(f"Cannot order more than available stock: {stock.quantity}", status=400)

                # Уменьшаем количество на складе после всех проверок
                for item in cart_items:
                    stock = Stock.objects.get(product=item.product)
                    stock.quantity -= item.quantity
                    stock.save()
                    env_logger.debug(f"Updated stock for product {item.product.name}: new quantity {stock.quantity}")

                # Создаем заказ для выбранной корзины
                order = Order.objects.create(
                    customer=customer,
                    cart=cart,
                    delivery_datetime=delivery_datetime,
                    status=Order.OrderStatus.PENDING
                )
                env_logger.debug(f"Order created: {order}")

                # Создаем запись в истории покупок
                for item in cart_items:
                    PurchaseHistory.objects.create(
                        customer=customer,
                        product=item.product,
                        quantity=item.quantity,
                        order=order,
                        purchase_date=order.order_date
                    )
                    env_logger.debug(f"Purchase history created for order {order.id}")

                return redirect('order_success')
            except ValidationError as e:
                env_logger.error(f"Validation error: {e}")
                return HttpResponse(f"Error: {e}", status=400)
            except Exception as e:
                env_logger.error(f"Unexpected error: {e}")
                return HttpResponse(f"Error: {e}", status=500)
        else:
            env_logger.error("Form is not valid")
            env_logger.debug(form.errors)
    else:
        env_logger.debug("Request method is not POST")
        form = OrderForm()
        form.fields['cart'].queryset = Cart.objects.filter(customer=request.user)

    return render(request, 'place_order.html', {'form': form})


def order_success(request):
    return render(request, 'order_success.html')


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
