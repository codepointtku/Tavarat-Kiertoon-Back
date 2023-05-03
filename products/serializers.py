from rest_framework import serializers

from .models import Color, ModifyProduct, Picture, Product, Storage


class PictureSerializer(serializers.ModelSerializer):
    picture_address = serializers.SerializerMethodField()

    def get_picture_address(self, obj):
        return obj.picture_address.name

    class Meta:
        model = Picture
        fields = "__all__"


class ModifyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModifyProduct
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    color_name = serializers.ReadOnlyField(source="color.name")
    storage_name = serializers.ReadOnlyField(source="storages.name")
    pictures = PictureSerializer(many=True, read_only=True)
    modified = ModifyProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"
