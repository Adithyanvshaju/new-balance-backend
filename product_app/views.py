
from rest_framework import generics

from .models import Product
from .serializers import ProductSerializer
from .pagination import ProductPagination


class ProductListAPIView(generics.ListAPIView):

    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):

        queryset = Product.objects.select_related('category').all()

        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        gender = self.request.query_params.get('gender')
        ordering = self.request.query_params.get('ordering')

        if category:
            queryset = queryset.filter(
                category__name__iexact=category
            )

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        if gender:
            queryset = queryset.filter(
                gender__iexact=gender
            )

        if ordering == 'price':
            queryset = queryset.order_by('price')

        elif ordering == '-price':
            queryset = queryset.order_by('-price')

        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):

    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

