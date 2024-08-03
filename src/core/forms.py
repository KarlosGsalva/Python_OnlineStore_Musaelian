from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from .models import Customer, Product, Stock, Cart, Order, Category

User = get_user_model()


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


class CustomerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, help_text="Enter a password")
    password2 = forms.CharField(widget=forms.PasswordInput, help_text="Enter the password again for confirmation")

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'address', 'contact_info', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.password = make_password(self.cleaned_data["password1"])
        if commit:
            customer.save()
        return customer
