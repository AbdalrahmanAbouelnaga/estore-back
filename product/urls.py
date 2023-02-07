from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path


urlpatterns = [
    path('latest-products/',views.LatestProducts.as_view(),name='latest_products'),
    path('categories/',views.CategoryAPI.as_view(),name='category-list'),
    path('<slug:subcategory_slug>/products/',views.ProductsAPI.as_view({"get":"list"}),name='product-list'),
    path('product/<slug:product_slug>/',views.ProductsAPI.as_view({"get":"retrieve"}),name='product-detail')
]