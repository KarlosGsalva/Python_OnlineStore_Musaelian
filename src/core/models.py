from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    address = models.TextField()
    contact_info = models.TextField()

    class Meta:
        db_table = "customers"
        verbose_name = "customers"
        verbose_name_plural = "customers"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = "products"
        verbose_name = "products"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "stock"
        verbose_name = "stock"
        verbose_name_plural = "stock"

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "cart"
        verbose_name = "cart"
        verbose_name_plural = "cart"

    def __str__(self):
        return f"{self.customer.first_name}'s cart"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=255)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders"
        verbose_name = "orders"
        verbose_name_plural = "orders"

    def __str__(self):
        return f"Order {self.id} by {self.customer.first_name}"


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "categories"
        verbose_name = "categories"
        verbose_name_plural = "categories"
