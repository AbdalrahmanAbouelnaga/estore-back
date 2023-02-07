from rest_framework import serializers
from .models import Category,SubCategory,ProductSpec,ProductImages,Product
from django.urls import reverse

class SubCategorySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self,obj):
        return reverse('product-list',kwargs={"subcategory_slug":obj.slug})

    class Meta:
        model = SubCategory
        fields = (
            'url',
            'title',
        )

class CategorySerializer(serializers.ModelSerializer):
    sub_categories = SubCategorySerializer(many=True)
    class Meta:
        model = Category
        fields = (
            'title',
            'sub_categories'

        )


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = (
            'image',
        )

class ProductThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = (
            'thumbnail',
        )

class ProductSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpec
        fields = (
            'title',
            'desc'
        )


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductThumbnailSerializer(many=True)
    class Meta:
        model = Product
        fields = (
            'title',
            'in_stock',
            'price',
            'images'
        )

class ProductDetailSerializer(serializers.ModelSerializer):
    specs = ProductSpecSerializer(many=True)
    images = ProductImageSerializer(many=True)
    category = serializers.SerializerMethodField()
    sub_category = serializers.SlugRelatedField('title',read_only=True)
    url = serializers.SerializerMethodField()

    def get_url(self,obj):
        return reverse('product-detail',kwargs={"product_slug":obj.slug})

    def get_category(self,obj):
        return obj.sub_category.category.title
    class Meta:
        model = Product
        fields = (
            'url',
            'title',
            'in_stock',
            'category',
            'sub_category',
            'price',
            'images',
            'specs'
        )

