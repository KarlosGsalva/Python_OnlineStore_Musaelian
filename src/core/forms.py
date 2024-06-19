from django import forms
from .models import Customer, Product, Stock, Cart, Order, Category


class CartForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField(min_value=1)


class OrderForm(forms.Form):
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    email = forms.EmailField()
    cart = forms.ModelChoiceField(queryset=Cart.objects.all())


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
