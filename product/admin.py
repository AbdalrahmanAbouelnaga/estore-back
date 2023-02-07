from django.contrib import admin
from .models import Product,ProductImages,ProductSpec,Category,SubCategory
# Register your models here.


admin.site.register(Category)
admin.site.register(SubCategory)


class SpecInline(admin.TabularInline):
    model = ProductSpec

class ImageInline(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    model = Product
    inlines = (
        SpecInline,
        ImageInline
    )

admin.site.register(Product,ProductAdmin)