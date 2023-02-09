from . import views
from django.urls import path


urlpatterns = [
    path('cart/',views.CartAPI.as_view(),name='cart'),
    path('cart/add-to-cart/',views.AddToCartAPI.as_view(),name='addToCart'),
    path('cart/remove-from-cart/',views.RemoveFromCartAPI.as_view(),name='removeFromCart'),
    path('cart/change-item-quantity/',views.ItemQuantityAPI.as_view()),
    path('checkout/paymob/',views.paymob_payment),
    path('checkout/stripe/',views.StripePayment)
]