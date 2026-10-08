from django.urls import path
from .views import (
    CreateOrderAPIView,
    OrderListAPIView
)

urlpatterns = [
    path(
        'orders/create/',
        CreateOrderAPIView.as_view(),
        name='create-order'
    ),

    path(
        'orders/',
        OrderListAPIView.as_view(),
        name='order-list'
    ),
]