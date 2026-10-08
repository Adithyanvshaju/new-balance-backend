from django.urls import path

from .views import (
    AddToWishlistAPIView,
    WishlistAPIView,
    RemoveFromWishlistAPIView
)


urlpatterns = [

    path(
        'wishlist/add/',
        AddToWishlistAPIView.as_view(),
        name='add-to-wishlist'
    ),

    path(
        'wishlist/',
        WishlistAPIView.as_view(),
        name='wishlist'
    ),

    path(
        'wishlist/<int:product_id>/',
        RemoveFromWishlistAPIView.as_view(),
        name='remove-from-wishlist'
    ),
]