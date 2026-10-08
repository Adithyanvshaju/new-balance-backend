import razorpay

from django.conf import settings
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from order_app.models import Order
from .models import Payment


class CreatePaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        order_id = request.data.get('order_id')

        if not order_id:
            return Response(
                {"error": "Order ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != 'pending':
            return Response(
                {"error": "This order cannot be paid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a Razorpay payment was already created
        try:
            payment = Payment.objects.get(order=order)

            return Response(
                {
                    "payment_id": payment.id,
                    "razorpay_order_id": payment.razorpay_order_id,
                    "amount": int(payment.amount * 100),
                    "currency": "INR",
                    "key_id": settings.RAZORPAY_KEY_ID
                },
                status=status.HTTP_200_OK
            )

        except Payment.DoesNotExist:
            pass

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        amount_in_paise = int(order.total_amount * 100)

        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_{order.id}"
        })

        payment = Payment.objects.create(
            user=request.user,
            order=order,
            razorpay_order_id=razorpay_order['id'],
            amount=order.total_amount,
            status='created'
        )

        return Response(
            {
                "payment_id": payment.id,
                "razorpay_order_id": razorpay_order['id'],
                "amount": amount_in_paise,
                "currency": "INR",
                "key_id": settings.RAZORPAY_KEY_ID
            },
            status=status.HTTP_201_CREATED
        )


class VerifyPaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        razorpay_order_id = request.data.get(
            'razorpay_order_id'
        )

        razorpay_payment_id = request.data.get(
            'razorpay_payment_id'
        )

        razorpay_signature = request.data.get(
            'razorpay_signature'
        )

        if (
            not razorpay_order_id
            or not razorpay_payment_id
            or not razorpay_signature
        ):
            return Response(
                {"error": "Payment details are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.select_related(
                'order'
            ).get(
                razorpay_order_id=razorpay_order_id,
                user=request.user
            )

        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prevent duplicate processing
        if payment.status == 'paid':
            return Response(
                {"message": "Payment already verified"},
                status=status.HTTP_200_OK
            )

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

        except razorpay.errors.SignatureVerificationError:

            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # with transaction.atomic():

        #     order = payment.order
        with transaction.atomic():

            print("VERIFY PAYMENT CALLED")
            print("ORDER:", payment.order.id)

            order = payment.order   

            # Reduce stock
            for order_item in order.items.select_related(
                'product'
            ):

                product = order_item.product

                if order_item.quantity > product.stock:

                    return Response(
                        {
                            "error": (
                                f"Not enough stock for "
                                f"{product.name}"
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                product.stock -= order_item.quantity
                product.save()

                print(
                    "STOCK UPDATED:",
                    product.name,
                    product.stock
                )

            # Mark payment as paid
            payment.razorpay_payment_id = razorpay_payment_id
            payment.status = 'paid'
            payment.save()

            # Mark order as paid
            order.status = 'paid'
            order.save()

            # Clear cart
            try:
                cart = request.user.cart
                cart.items.all().delete()
            except Exception:
                pass

        return Response(
            {
                "message": "Payment verified successfully",
                "order_id": order.id,
                "status": order.status
            },
            status=status.HTTP_200_OK
        )