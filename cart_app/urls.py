from django.urls import path

from .views import (
    AddToCartAPIView,
    CartAPIView,
    CartItemUpdateAPIView
)

urlpatterns = [
    path(
        'cart/add/',
        AddToCartAPIView.as_view(),
        name='add-to-cart'
    ),

    path(
        'cart/',
        CartAPIView.as_view(),
        name='cart'
    ),

    path(
        'cart/items/<int:item_id>/',
        CartItemUpdateAPIView.as_view(),
        name='cart-item-update'
    ),
]