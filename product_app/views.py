
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer
from .pagination import ProductPagination


# Customer product listing, search, filters, and sorting
class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = Product.objects.select_related("category").filter(
            is_active=True
        )

        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")
        gender = self.request.query_params.get("gender")
        ordering = self.request.query_params.get("ordering")

        if category:
            queryset = queryset.filter(category__name__iexact=category)

        if search:
            queryset = queryset.filter(name__icontains=search)

        if gender:
            queryset = queryset.filter(gender__iexact=gender)

        if ordering == "price":
            queryset = queryset.order_by("price")
        elif ordering == "-price":
            queryset = queryset.order_by("-price")

        return queryset


# Customer product details
# Inactive products return 404
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("category").filter(
        is_active=True
    )
    serializer_class = ProductSerializer


# Admin product listing
# Includes active and inactive products
class AdminProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.select_related("category").all().order_by("id")
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [IsAdminUser]


# Admin block/unblock product
class ProductToggleStatusAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        product.is_active = not product.is_active
        product.save(update_fields=["is_active"])

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_200_OK
        )


# Admin view and update product
class AdminProductDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
