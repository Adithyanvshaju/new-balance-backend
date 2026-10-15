
from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination

from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart_app.models import Cart


class CreateOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_items = cart.items.select_related("product")

        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = Decimal("0.00")

        for cart_item in cart_items:

            product = cart_item.product

            # Prevent purchasing blocked products
            if not product.is_active:
                return Response(
                    {
                        "error": (
                            f"{product.name} is no longer available. "
                            "Please remove it from your cart."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check available stock
            if cart_item.quantity > product.stock:
                return Response(
                    {
                        "error": f"Not enough stock for {product.name}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_amount += product.price * cart_item.quantity

        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status="pending"
        )

        for cart_item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class OrderListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related(
            "items__product",
            "items__product__category"
        ).order_by("-created_at")

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)


class AdminOrderPagination(PageNumberPagination):
    page_size = 10


class AdminOrderListAPIView(generics.ListAPIView):

    permission_classes = [IsAdminUser]
    serializer_class = OrderSerializer
    pagination_class = AdminOrderPagination

    def get_queryset(self):

        return (
            Order.objects.select_related("user")
            .prefetch_related(
                "items__product",
                "items__product__category"
            )
            .order_by("-created_at")
        )


class AdminUpdateOrderStatusAPIView(APIView):

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):

        try:
            order = Order.objects.get(pk=pk)

        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")

        allowed_statuses = [
            value for value, label in Order.STATUS_CHOICES
        ]

        if new_status not in allowed_statuses:
            return Response(
                {
                    "detail": "Invalid order status.",
                    "allowed_statuses": allowed_statuses
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data)
