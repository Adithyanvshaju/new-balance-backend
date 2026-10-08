from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Wishlist
from .serializers import WishlistSerializer
from product_app.models import Product


class AddToWishlistAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        product_id = request.data.get('product')

        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            return Response(
                {"message": "Product already in wishlist"},
                status=status.HTTP_200_OK
            )

        serializer = WishlistSerializer(wishlist_item)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class WishlistAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related(
            'product',
            'product__category'
        )

        serializer = WishlistSerializer(
            wishlist_items,
            many=True
        )

        return Response(serializer.data)


class RemoveFromWishlistAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):

        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                product_id=product_id
            )
        except Wishlist.DoesNotExist:
            return Response(
                {"error": "Product is not in wishlist"},
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist_item.delete()

        return Response(
            {"message": "Product removed from wishlist"},
            status=status.HTTP_200_OK
        )