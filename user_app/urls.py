
from django.urls import path

from .views import (
    RegisterAPIView,
    LoginAPIView,
    ProfileAPIView,
    VerifyOTPAPIView,
    AdminLoginAPIView,
    AdminUserListAPIView,
    AdminUserDetailAPIView,
    AdminAddProductAPIView,
    AdminUserToggleBlockAPIView,
    AdminDashboardStatsAPIView,
)

urlpatterns = [
    
    path(
        "register/",
        RegisterAPIView.as_view(),
        name="register",
    ),
    path(
        "login/",
        LoginAPIView.as_view(),
        name="login",
    ),
    path(
        "verify-otp/",
        VerifyOTPAPIView.as_view(),
        name="verify-otp",
    ),
    path(
        "profile/",
        ProfileAPIView.as_view(),
        name="profile",
    ),

   
    path(
        "admin/login/",
        AdminLoginAPIView.as_view(),
        name="admin-login",
    ),

    
    path(
        "admin/stats/",
        AdminDashboardStatsAPIView.as_view(),
        name="admin-stats",
    ),

   
    path(
        "admin/users/",
        AdminUserListAPIView.as_view(),
        name="admin-users",
    ),
    path(
        "admin/users/<int:pk>/toggle-block/",
        AdminUserToggleBlockAPIView.as_view(),
        name="admin-user-toggle-block",
    ),
    path(
        "admin/users/<int:pk>/",
        AdminUserDetailAPIView.as_view(),
        name="admin-user-detail",
    ),

    
    path(
        "admin/products/add/",
        AdminAddProductAPIView.as_view(),
        name="admin-add-product",
    ),
]