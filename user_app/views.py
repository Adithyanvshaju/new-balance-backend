
import random
from datetime import timedelta

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializer import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    AdminLoginSerializer,
    AdminUserSerializer,
)

from .models import EmailOTP, PendingUser
from product_app.models import Product as StoreProduct
from product_app.models import Category
from product_app.serializers import ProductSerializer as StoreProductSerializer
from order_app.models import Order



class RegisterAPIView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            
            if User.objects.filter(username=username).exists():
                return Response(
                    {"message": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            if User.objects.filter(email=email).exists():
                return Response(
                    {"message": "Email already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            PendingUser.objects.filter(email=email).delete()

            
            otp = str(random.randint(100000, 999999))

            
            PendingUser.objects.create(
                username=username,
                email=email,
                password=password
            )

            
            EmailOTP.objects.create(
                email=email,
                otp=otp
            )

            send_mail(
                'New Balance Email Verification OTP',
                f'Your OTP is {otp}. It is valid for 5 minutes.',
                None,
                [email],
            )

            return Response(
                {"message": "OTP sent to your email"},
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

        if not email or not otp:
            return Response(
                {"message": "Email and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            otp_record = EmailOTP.objects.filter(
                email=email,
                otp=otp
            ).latest('created_at')
        except EmailOTP.DoesNotExist:
            return Response(
                {"message": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() - otp_record.created_at > timedelta(minutes=5):
            otp_record.delete()
            return Response(
                {"message": "OTP has expired. Please register again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pending_user = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response(
                {"message": "Registration data not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=pending_user.username).exists():
            return Response(
                {"message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        User.objects.create_user(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password
        )

        pending_user.delete()
        EmailOTP.objects.filter(email=email).delete()

        return Response(
            {"message": "Email verified and user registered successfully"},
            status=status.HTTP_201_CREATED
        )


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "You are logged in",
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff
        })


class AdminLoginAPIView(TokenObtainPairView):
    serializer_class = AdminLoginSerializer



class AdminUserListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.filter(
            is_staff=False,
            is_superuser=False
        ).order_by('-date_joined')

        serializer = AdminUserSerializer(users, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )




class AdminUserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_customer(self, pk):
        return User.objects.filter(
            pk=pk,
            is_staff=False,
            is_superuser=False
        ).first()

    def get(self, request, pk):
        user = self.get_customer(pk)

        if user is None:
            return Response(
                {"message": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AdminUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user = self.get_customer(pk)

        if user is None:
            return Response(
                {"message": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.delete()

        return Response(
            {"message": "Customer deleted successfully"},
            status=status.HTTP_200_OK
        )





class AdminAddProductAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        data = request.data.copy()

        category_name = data.get("category")

        if not category_name or not str(category_name).strip():
            return Response(
                {"category": ["Please enter a category."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        category_name = str(category_name).strip()

        category, created = Category.objects.get_or_create(
            name=category_name
        )

        
        data["category"] = category.name

        serializer = StoreProductSerializer(data=data)

        if serializer.is_valid():
            product = serializer.save()

            return Response(
                {
                    "message": "Product added successfully",
                    "product": StoreProductSerializer(product).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )




class AdminUserDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        try:
            user = User.objects.get(
                pk=pk,
                is_staff=False,
                is_superuser=False
            )
        except User.DoesNotExist:
            return Response(
                {"message": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.delete()

        return Response(
            {"message": "Customer deleted successfully"},
            status=status.HTTP_200_OK
        )


class AdminUserToggleBlockAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:
            user = User.objects.get(
                pk=pk,
                is_staff=False,
                is_superuser=False
            )
        except User.DoesNotExist:
            return Response(
                {"message": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])

        return Response(
            {
                "message": (
                    "Customer blocked successfully"
                    if not user.is_active
                    else "Customer unblocked successfully"
                ),
                "id": user.id,
                "is_active": user.is_active
            },
            status=status.HTTP_200_OK
        )


class AdminDashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        
        total_users = User.objects.filter(
            is_staff=False,
            is_superuser=False
        ).count()

        
        total_products = StoreProduct.objects.count()

        
        total_orders = Order.objects.count()

        
        paid_orders = Order.objects.filter(status="paid")

        pending_orders = Order.objects.filter(
            status="pending"
        ).count()

        cancelled_orders = Order.objects.filter(
            status="cancelled"
        ).count()

        
        total_revenue = (
            paid_orders.aggregate(
                revenue=Sum("total_amount")
            )["revenue"] or 0
        )

        six_months_ago = timezone.now() - timedelta(days=180)

        monthly_sales = (
    Order.objects.filter(created_at__gte=six_months_ago)
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(
        orders=Count("id"),
        revenue=Sum(
            "total_amount",
            filter=Q(status="paid"),
        ),
    )
    .order_by("month")
)

        sales_chart = [
    {
        "month": item["month"].strftime("%b %Y"),
        "revenue": float(item["revenue"] or 0),
        "orders": item["orders"],
    }
    for item in monthly_sales
]

        return Response({
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "paid_orders": paid_orders.count(),
            "pending_orders": pending_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": float(total_revenue),
            "monthly_sales": sales_chart,
        }, status=status.HTTP_200_OK)