from django.urls import path

from .views import (
    CreateOrderAPIView,
    OrderListAPIView,
    AdminOrderListAPIView,
    AdminUpdateOrderStatusAPIView,
)

urlpatterns = [
    # Customer order APIs
    path(
        "orders/create/",
        CreateOrderAPIView.as_view(),
        name="create-order",
    ),
    path(
        "orders/",
        OrderListAPIView.as_view(),
        name="order-list",
    ),

    # Admin order APIs
    path(
        "admin/orders/",
        AdminOrderListAPIView.as_view(),
        name="admin-order-list",
    ),
    path(
        "admin/orders/<int:pk>/update-status/",
        AdminUpdateOrderStatusAPIView.as_view(),
        name="admin-update-order-status",
    ),
]