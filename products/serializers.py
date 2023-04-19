from rest_framework import serializers

from .models import Color, Picture, Product, Storage


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    color_name = serializers.ReadOnlyField(source="color.name")
    storage_name = serializers.ReadOnlyField(source="storages.name")

    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ("__all__")


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = "__all__"


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"
