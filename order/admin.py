from django.contrib import admin
from .models import Order,OrderItem,Cart,CartItem
# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem

class OrderAdmin(admin.ModelAdmin):
    model = Order
    inlines = (
        OrderItemInline,
    )

class CartAdmin(admin.ModelAdmin):
    model = Cart
    inlines = (
        CartItemInline,
    )

admin.site.register(Order,OrderAdmin)
admin.site.register(Cart,CartAdmin)