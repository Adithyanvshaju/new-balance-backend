
import random

from django.core.mail import send_mail
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializer import (
    RegisterSerializer,
    AdminLoginSerializer,
    AdminUserSerializer
)
from .models import EmailOTP, PendingUser


class RegisterAPIView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return Response(
                    {
                        "message": "Username already exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return Response(
                    {
                        "message": "Email already exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Remove old pending registration for this email
            PendingUser.objects.filter(email=email).delete()

            # Create OTP
            otp = str(random.randint(100000, 999999))

            # Store registration details temporarily
            PendingUser.objects.create(
                username=username,
                email=email,
                password=password
            )

            # Store OTP
            EmailOTP.objects.create(
                email=email,
                otp=otp
            )

            # Send OTP
            send_mail(
                'New Balance Email Verification OTP',
                f'Your OTP is {otp}. It is valid for 5 minutes.',
                None,
                [email],
            )

            return Response(
                {
                    "message": "OTP sent to your email"
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class VerifyOTPAPIView(APIView):

    def post(self, request):

        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            otp_record = EmailOTP.objects.filter(
                email=email,
                otp=otp
            ).latest('created_at')

        except EmailOTP.DoesNotExist:
            return Response(
                {
                    "message": "Invalid OTP"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pending_user = PendingUser.objects.get(email=email)

        except PendingUser.DoesNotExist:
            return Response(
                {
                    "message": "Registration data not found"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the actual Django user
        User.objects.create_user(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password
        )

        # Delete temporary data
        pending_user.delete()
        otp_record.delete()

        return Response(
            {
                "message": "Email verified and user registered successfully"
            },
            status=status.HTTP_201_CREATED
        )


class ProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "message": "You are logged in",
            "username": request.user.username,
            "email": request.user.email
        })


class AdminLoginAPIView(TokenObtainPairView):

    serializer_class = AdminLoginSerializer


class AdminUserListAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):

        users = User.objects.all().order_by('-date_joined')

        serializer = AdminUserSerializer(users, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class AdminUserDetailAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):

        try:
            user = User.objects.get(pk=pk)

        except User.DoesNotExist:
            return Response(
                {
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AdminUserSerializer(user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

