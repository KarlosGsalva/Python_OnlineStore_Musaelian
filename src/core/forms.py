from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Customer, Product, Stock, Cart, Order, Category


class CartForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField()

    # class Meta:
    #     model = Cart
    #     fields = ["customer", "product", "quantity"]


class OrderForm(forms.ModelForm):
    name = forms.CharField()
    adress = forms.CharField()
    email = forms.EmailField()
    cart = forms.ModelChoiceField(queryset=Cart.objects.all())

    # class Meta:
    #     model = Order
    #     fields = ["customer", "product", "quantity", "status"]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'address', 'contact_info']


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


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
