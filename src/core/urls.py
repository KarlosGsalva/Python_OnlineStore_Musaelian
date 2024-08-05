from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (
    product_list,
    add_to_cart,
    product_detail,
    create_customer,
    register,
    home_view,
    edit_customer,
    place_order,
    order_success
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(next_page='/login/', template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('products/', product_list, name='product_list'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('customers/create/', create_customer, name='create_customer'),
    path('customers/<int:pk>/edit/', edit_customer, name='edit_customer'),
    path('place_order/', place_order, name='place_order'),
    path('order_success/', order_success, name='order_success')
]
