import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    password = models.CharField()
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customer_users",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customer_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    objects = CustomerManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "customers"
        verbose_name = "customers"
        verbose_name_plural = "customers"

    def __str__(self):
        return self.email


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        verbose_name = "products"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock"
        verbose_name = "stock"
        verbose_name_plural = "stock"

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"
        verbose_name = "cart"
        verbose_name_plural = "carts"

    def __str__(self):
        return f"{self.customer.first_name or self.customer.email}'s cart"


class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "cart_item"
        verbose_name = "cart item"
        verbose_name_plural = "cart items"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.id}"


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PD", "Pending"  # заказ создан, но еще не обработан
        PROCESSING = "PR", "Processing"  # заказ обрабатывается
        AWAIT_PAYMENT = "PA", "Payment"  # заказ создан, но ожидается оплата
        SHIPPED = "SH", "Shipped"  # заказ отправлен клиенту
        DELIVERED = "DL", "Delivered"  # заказ доставлен клиенту
        CANCELED = "CC", "Canceled"  # заказ отменен
        RETURNED = "RT", "Returned"  # заказ возвращен клиентом
        COMPLETED = "CL", "Completed"  # заказ полностью выполнен и закрыт

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_datetime = models.DateTimeField(
        help_text="Date and time of delivery", default=timezone.now
    )
    status = models.CharField(
        max_length=8, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )

    class Meta:
        db_table = "orders"
        verbose_name = "orders"
        verbose_name_plural = "orders"

    def __str__(self):
        return f"Order {self.id} by {self.customer.first_name or self.customer.email}"

    def save(self, *args, **kwargs):
        # Проверка наличия товара на складе для каждого элемента корзины
        cart_items = CartItem.objects.filter(cart=self.cart)
        for item in cart_items:
            stock = Stock.objects.get(product=item.product)
            if item.quantity > stock.quantity:
                raise ValidationError(
                    f"Cannot order more than available stock: {stock.quantity}"
                )

        super(Order, self).save(*args, **kwargs)
        # Создание записей в истории покупок для каждого элемента корзины
        for item in cart_items:
            PurchaseHistory.objects.create(
                customer=self.customer,
                product=item.product,
                quantity=item.quantity,
                order=self,
                purchase_date=(
                    self.delivery_datetime
                    if self.delivery_datetime
                    else self.order_date
                ),
            )


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "categories"
        verbose_name = "categories"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class PurchaseHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField()

    class Meta:
        db_table = "purchase_history"
        verbose_name = "purchase_history"
        verbose_name_plural = "purchase_histories"

    def __str__(self):
        return f"Purchase of {self.product.name} by {self.customer.first_name} on {self.purchase_date}"
