from django.contrib import admin
from django.urls import path, include
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.books, name='books'),
    path('shoes/', views.shoes, name='shoes'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/', views.profile, name='profile'),
    path('write_review/<str:category>/<int:product_id>/', views.write_review, name='write_review'),
    path('view_reviews/<str:category>/<int:product_id>/', views.view_reviews, name='view_reviews'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('support_dashboard/', views.support_dashboard, name='support_dashboard'),
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('order_history/', views.order_history, name='order_history'),
    path('respond_query/<int:query_id>/', views.respond_query, name='respond_query'),
    path('fulfill_order/<int:order_id>/', views.fulfill_order, name='fulfill_order'),
    path('support/', views.support, name='support'),
    path('create_password/', views.create_password, name='create_password'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
]