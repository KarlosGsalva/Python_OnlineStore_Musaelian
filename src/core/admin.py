from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Product, Stock, Cart, Order

admin.site.register(User, UserAdmin)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Cart)
admin.site.register(Order)
