
from django.urls import path

from .views import (
    ProductListAPIView,
    ProductDetailAPIView,
    AdminProductListAPIView,
    ProductToggleStatusAPIView,
    AdminProductDetailAPIView
)


urlpatterns = [
    path(
        'products/',
        ProductListAPIView.as_view(),
        name='product-list'
    ),
    path(
    'products/<int:pk>/',
    ProductDetailAPIView.as_view(),
    name='product-detail'
),
    path(
        'admin/products/',
        AdminProductListAPIView.as_view(),
        name='admin-product-list'
    ),
    path(
    'products/<int:pk>/toggle-status/',
     ProductToggleStatusAPIView.as_view(),
     name='product-toggle-status'
),
path(
    "admin/products/<int:pk>/",
    AdminProductDetailAPIView.as_view(),
    name="admin-product-detail",
),
]

