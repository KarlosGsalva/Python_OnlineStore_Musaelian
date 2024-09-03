from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Customer


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            customer = Customer.objects.get(email=email)
            if customer and check_password(password, customer.password):
                return customer
        except Customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None
