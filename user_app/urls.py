
from django.urls import path

from .views import (
    RegisterAPIView,
    ProfileAPIView,
    VerifyOTPAPIView,
    AdminLoginAPIView,
    AdminUserListAPIView,
    AdminUserDetailAPIView,
)


urlpatterns = [

    path(
        'register/',
        RegisterAPIView.as_view(),
        name='register'
    ),

    path(
        'verify-otp/',
        VerifyOTPAPIView.as_view(),
        name='verify-otp'
    ),

    path(
        'profile/',
        ProfileAPIView.as_view(),
        name='profile'
    ),

    path(
        'admin/login/',
        AdminLoginAPIView.as_view(),
        name='admin-login'
    ),

    path(
        'admin/users/',
        AdminUserListAPIView.as_view(),
        name='admin-users'
    ),

    path(
        'admin/users/<int:pk>/',
        AdminUserDetailAPIView.as_view(),
        name='admin-user-detail'
    ),

]

