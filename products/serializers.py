from rest_framework import serializers

from .models import Color, Picture, Product, ProductItem, Storage


class PictureSerializer(serializers.ModelSerializer):
    picture_address = serializers.SerializerMethodField()

    def get_picture_address(self, obj) -> str:
        return obj.picture_address.name

    class Meta:
        model = Picture
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    color_name = serializers.ReadOnlyField(source="color.name")
    storage_name = serializers.ReadOnlyField(source="storages.name")
    pictures = PictureSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductUpdateSerializer(serializers.ModelSerializer):
    modify_date = serializers.CharField(required=False)

    class Meta:
        model = Product
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    color_name = serializers.ReadOnlyField(source="color.name")
    storage_name = serializers.ReadOnlyField(source="storages.name")
    pictures = PictureSerializer(many=True, read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "available": {"required": True},
            "barcode": {"required": True},
            "group_id": {"required": True},
            "price": {"required": True},
            "shelf_id": {"required": True},
            "free_description": {"required": True},
            "modified_date": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},
            "category": {"required": True},
            "storages": {"required": True},
            "color": {"required": True},
        }


class ProductStorageListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    color_name = serializers.ReadOnlyField(source="color.name")
    storage_name = serializers.ReadOnlyField(source="storages.name")
    pictures = PictureSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "available": {"required": True},
            "barcode": {"required": True},
            "group_id": {"required": True},
            "price": {"required": True},
            "shelf_id": {"required": True},
            "free_description": {"required": True},
            "modified_date": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},
            "category": {"required": True},
            "storages": {"required": True},
            "color": {"required": True},
        }


class ProductColorStringSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    color = serializers.CharField()
    pictures = serializers.FileField()

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "available": {"required": True},
            "barcode": {"required": True},
            "category": {"required": True},
            "storages": {"required": True},
            "color": {"required": True},
        }


class ProductCreateSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    pictures = serializers.FileField()
    color = serializers.IntegerField()

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "available": {"required": True},
            "barcode": {"required": True},
            "category": {"required": True},
            "storages": {"required": True},
            "color": {"required": True},
        }


class ProductStorageTransferSerializer(serializers.Serializer):
    storage = serializers.IntegerField()
    products = serializers.ListField(child=serializers.IntegerField())


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"


class ShoppingCartAvailableAmountListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class ProductItemsSerializer(serializers.ModelSerializer):
    """
    serializer for product items
    """

    product = ProductSerializer(read_only=True)
    storage = StorageSerializer(read_only=True)

    class Meta:
        model = ProductItem
        fields = "__all__"


class ProductItemUpdateSerializer(serializers.ModelSerializer):
    """
    serializer for product items
    """

    class Meta:
        model = ProductItem
        fields = "__all__"
        extra_kwargs = {
            "modified_date": {"read_only": True},
        }
