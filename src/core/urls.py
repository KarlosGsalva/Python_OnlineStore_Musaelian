from django.contrib.auth import views as auth_views
from django.urls import path
from .views import product_list, add_to_cart, product_detail, create_customer, register, home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('products/', product_list, name='product_list'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('create_customer/', create_customer, name='create_customer'),
    path('register/', register, name='register'),
]
