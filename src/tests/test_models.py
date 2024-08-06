from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.models import Product, Stock, Customer, Cart, CartItem, Order


class ProductTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product", price=10, description="A test product"
        )
        self.customer = Customer.objects.create(
            email="test@example.com", first_name="Test", last_name="Customer"
        )
        self.cart = Cart.objects.create(customer=self.customer)
        self.stock = Stock.objects.create(product=self.product, quantity=10)

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 10)

    def test_stock_quantity(self):
        self.assertEqual(self.stock.quantity, 10)

    def test_add_to_cart(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=3
        )
        self.assertEqual(cart_item.quantity, 3)
        self.assertEqual(cart_item.product.name, "Test Product")


class CustomerTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            email="customer@example.com", first_name="John", last_name="Doe"
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.email, "customer@example.com")
        self.assertEqual(self.customer.first_name, "John")
        self.assertEqual(self.customer.last_name, "Doe")


class OrderTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product", price=10, description="A test product"
        )
        self.customer = Customer.objects.create(
            email="test@example.com", first_name="Test", last_name="Customer"
        )
        self.cart = Cart.objects.create(customer=self.customer)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )
        self.stock = Stock.objects.create(product=self.product, quantity=10)

    def test_order_creation(self):
        self.order = Order.objects.create(
            customer=self.customer,
            cart=self.cart,
            status="PD",
            delivery_datetime=timezone.now(),
        )
        self.assertEqual(self.order.customer.email, "test@example.com")
        self.assertEqual(self.order.status, "PD")

    def test_order_stock_check(self):
        self.cart_item.quantity = 15
        self.cart_item.save()
        with self.assertRaises(ValidationError):
            self.order = Order.objects.create(
                customer=self.customer,
                cart=self.cart,
                status="PD",
                delivery_datetime=timezone.now(),
            )


class StockTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product", price=10, description="A test product"
        )
        self.stock = Stock.objects.create(product=self.product, quantity=20)

    def test_stock_creation(self):
        self.assertEqual(self.stock.product.name, "Test Product")
        self.assertEqual(self.stock.quantity, 20)

    def test_stock_update(self):
        self.stock.quantity = 15
        self.stock.save()
        self.assertEqual(self.stock.quantity, 15)

    def test_stock_str(self):
        self.assertEqual(str(self.stock), "Test Product - 20")


class CartTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            email="customer@example.com", first_name="John", last_name="Doe"
        )
        self.cart = Cart.objects.create(customer=self.customer)

    def test_cart_creation(self):
        self.assertEqual(self.cart.customer.email, "customer@example.com")
        self.assertEqual(str(self.cart), "John's cart")

    def test_cart_str_with_email(self):
        self.customer.first_name = ""
        self.customer.save()
        self.assertEqual(str(self.cart), "customer@example.com's cart")


class CartItemTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product", price=10, description="A test product"
        )
        self.customer = Customer.objects.create(
            email="customer@example.com", first_name="John", last_name="Doe"
        )
        self.cart = Cart.objects.create(customer=self.customer)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )

    def test_cart_item_creation(self):
        self.assertEqual(self.cart_item.product.name, "Test Product")
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(str(self.cart_item), "2 x Test Product in cart 1")

    def test_cart_item_update_quantity(self):
        self.cart_item.quantity = 5
        self.cart_item.save()
        self.assertEqual(self.cart_item.quantity, 5)
