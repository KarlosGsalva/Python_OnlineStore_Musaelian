from django.contrib import admin
from .models import Customer, Product, Stock, Cart, Order, Category

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Category)
