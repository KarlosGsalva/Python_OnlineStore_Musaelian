from django import forms
from .models import Customer, Product, Stock, Cart, Order, Category


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ["customer", "product", "quantity"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "product", "quantity", "status"]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'patronymic', 'address', 'contact_info']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category']


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product', 'quantity']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
