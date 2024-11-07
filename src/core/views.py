import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate


from .forms import (
    CartForm,
    CustomerForm,
    CustomerRegistrationForm,
    OrderForm,
    RemoveCartItemForm,
)
from .models import Cart, Product, Customer, Order, CartItem, PurchaseHistory, Stock

env_logger = logging.getLogger("env_logger")


def home_view(request):
    return render(request, "home.html")


def product_list(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {"product": product}
    return render(request, "product_detail.html", context)


@login_required
def add_to_cart(request):
    env_logger.debug("Entered add_to_cart view")

    if request.method == "POST":
        env_logger.debug("Request method is POST")

        form = CartForm(request.POST)

        if form.is_valid():
            env_logger.debug("Form is valid")

            user_email = request.user.email
            try:
                customer = Customer.objects.get(email=user_email)
            except Customer.DoesNotExist:
                env_logger.error(f"Customer with email {user_email} does not exist")
                return HttpResponse("Customer not found", status=404)

            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]

            env_logger.debug(
                f"Customer: {customer}, Product: {product}, Quantity: {quantity}"
            )

            # Проверка на наличие существующей корзины для клиента
            try:
                cart = Cart.objects.get(customer=customer)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(customer=customer)
            except Cart.MultipleObjectsReturned:
                cart = Cart.objects.filter(customer=customer).first()
                Cart.objects.filter(customer=customer).exclude(id=cart.id).delete()

            # Добавляем товар в корзину
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={"quantity": quantity}
            )
            if not created:
                cart_item.quantity += quantity
            cart_item.save()
            env_logger.debug(
                f"Cart item created: {created}, Quantity after update: {cart_item.quantity}"
            )

            return redirect("view_cart")
        else:
            env_logger.error("Form is not valid")
            env_logger.debug(form.errors)
    else:
        env_logger.debug("Request method is not POST")
        form = CartForm()

    return render(request, "add_to_cart.html", {"form": form})


@login_required
def place_order(request):
    env_logger.debug("Entered place_order view")

    if request.method == "POST":
        env_logger.debug("Request method is POST")

        form = OrderForm(request.POST)
        form.fields["cart"].queryset = Cart.objects.filter(customer=request.user)
        if form.is_valid():
            env_logger.debug("Form is valid")

            name = form.cleaned_data["name"]
            address = form.cleaned_data["address"]
            delivery_datetime = form.cleaned_data["delivery_datetime"]
            email = form.cleaned_data["email"]
            cart = form.cleaned_data["cart"]

            env_logger.debug(
                f"Name: {name}, "
                f"Address: {address}, "
                f"Email: {email}, "
                f"Delivery Date and Time: {delivery_datetime}, "
                f"Cart: {cart}"
            )

            try:
                customer = Customer.objects.get(email=email)
                env_logger.debug(f"Customer found: {customer}")
            except Customer.DoesNotExist:
                env_logger.error(f"Customer with email {email} does not exist")
                return HttpResponse("Customer not found", status=404)

            try:
                env_logger.debug("Entering cart_items processing")
                # Проверка и обновление количества на складе для каждого элемента корзины
                cart_items = CartItem.objects.filter(cart=cart)
                env_logger.debug(f"Cart items: {cart_items.count()} items found")
                for item in cart_items:
                    env_logger.debug(
                        f"Processing item: {item.product.name}, Quantity: {item.quantity}"
                    )
                    stock = Stock.objects.get(product=item.product)
                    env_logger.debug(
                        f"Stock for {item.product.name}: {stock.quantity} available"
                    )
                    if item.quantity > stock.quantity:
                        env_logger.error(
                            f"Cannot order more than available stock: {stock.quantity}"
                        )
                        return HttpResponse(
                            f"Cannot order more than available stock: {stock.quantity}",
                            status=400,
                        )

                # Создаем заказ для выбранной корзины
                order = Order.objects.create(
                    customer=customer,
                    cart=cart,
                    delivery_datetime=delivery_datetime,
                    status=Order.OrderStatus.PENDING,
                )
                env_logger.debug(f"Order created: {order}")

                # Уменьшаем количество на складе после создания заказа
                for item in cart_items:
                    stock = Stock.objects.get(product=item.product)
                    stock.quantity -= item.quantity
                    stock.save()
                    env_logger.debug(
                        f"Updated stock for product {item.product.name}: new quantity {stock.quantity}"
                    )

                # Обновляем статус заказа на "PROCESSING"
                order.status = Order.OrderStatus.PROCESSING
                order.save()
                env_logger.debug(
                    f"Order status updated to PROCESSING for order {order.id}"
                )

                # Удаляем корзину
                cart.delete()
                env_logger.debug(f"Cart deleted for customer: {customer}")
                return redirect("order_success")
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
        form.fields["cart"].queryset = Cart.objects.filter(customer=request.user)

    return render(request, "place_order.html", {"form": form})


def order_success(request):
    return render(request, "order_success.html")


def create_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "create_customer.html", {"form": form})


def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)
    return render(request, "customer_form.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save()
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(request, email=customer.email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = CustomerRegistrationForm()
    return render(request, "register.html", {"form": form})


@login_required
def view_cart(request):
    cart = get_object_or_404(Cart, customer=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    remove_form = RemoveCartItemForm()

    if request.method == "POST":
        remove_form = RemoveCartItemForm(request.POST)
        if remove_form.is_valid():
            cart_item_id = remove_form.cleaned_data["cart_item_id"]
            cart_item = get_object_or_404(CartItem, id=cart_item_id)
            cart_item.delete()
            return redirect("view_cart")

    context = {"cart": cart, "cart_items": cart_items, "remove_form": remove_form}
    return render(request, "view_cart.html", context)


@login_required
def view_purchase_history(request):
    purchase_history = PurchaseHistory.objects.filter(customer=request.user).order_by(
        "-purchase_date"
    )
    env_logger.debug(
        f"Retrieved {purchase_history.count()} purchase history records for user {request.user.email}"
    )
    for purchase in purchase_history:
        env_logger.debug(f"Purchase: {purchase}")

    context = {"purchase_history": purchase_history}
    return render(request, "view_purchase_history.html", context)
