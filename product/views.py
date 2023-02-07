from .models import Category,Product
from .serializers import CategorySerializer,ProductListSerializer,ProductDetailSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,GenericAPIView
from rest_framework.response import Response

class CategoryAPI(ListAPIView,GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class ProductsAPI(ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    lookup_field = 'slug'
    def get_queryset(self):
        if self.action == 'list':
            return Product.objects.filter(sub_category__slug=self.kwargs["subcategory_slug"])
        else:
            return Product.objects.all()
    def get_object(self):
        return Product.objects.get(slug=self.kwargs["product_slug"])


class LatestProducts(APIView):
    def get(self,request,format='json'):
        data = Product.objects.all()[:25]
        serializer = ProductListSerializer(data=data)
        return Response(serializer.data,status=200)