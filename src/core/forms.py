from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from .models import Customer, Product, Stock, Cart, Category

User = get_user_model()


class CartForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label="Select Product")
    quantity = forms.IntegerField(min_value=1, error_messages={'required': 'Please enter a quantity',
                                                               'min_value': 'Quantity must be at least 1'})

    # class Meta:
    #     model = Cart
    #     fields = ["customer", "product", "quantity"]


class OrderForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    address = forms.CharField(label="Address", max_length=255)
    email = forms.EmailField(label="Email")
    delivery_datetime = forms.DateTimeField(
        label="Delivery Date and Time",
        widget=forms.TextInput(attrs={'type': 'datetime-local'})
    )
    cart = forms.ModelChoiceField(queryset=Cart.objects.none(), label="Cart")


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
