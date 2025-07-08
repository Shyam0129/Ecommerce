from django.contrib import admin
from .models import Product, Category, Cart, Order, Review, SupportQuery

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(SupportQuery)