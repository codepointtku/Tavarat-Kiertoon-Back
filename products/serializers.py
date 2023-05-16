from rest_framework import serializers

from .models import Color, Picture, Product, ProductItem, Storage


class PictureSerializer(serializers.ModelSerializer):
    picture_address = serializers.SerializerMethodField()

    def get_picture_address(self, obj) -> str:
        return obj.picture_address.name

    class Meta:
        model = Picture
        fields = "__all__"


class PictureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    pictures = PictureSerializer(many=True, read_only=True)
    amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_amount(self, obj):
        product_amount = ProductItem.objects.filter(product=obj.id, available=True).count()
        return product_amount

    def get_total_amount(self, obj):
        total_product_amount = ProductItem.objects.filter(product=obj.id).count()
        return total_product_amount


class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    product_item = ProductItemSerializer()
    pictures = PictureCreateSerializer(many=True, required=False)
    amount = serializers.IntegerField()

    class Meta:
        model = Product
        fields = "__all__"

    def create(self, validated_data):
        product_item = validated_data.pop("product_item")
        amount = validated_data.pop("amount")

        product = Product.objects.create(**validated_data)
        
        for i in range(amount):
            ProductItem.objects.create(product=product, **product_item)
            print(i)
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


# class ProductListSerializer(serializers.ModelSerializer):
#     category_name = serializers.ReadOnlyField(source="category.name")
#     color_name = serializers.ReadOnlyField(source="color.name")
#     storage_name = serializers.ReadOnlyField(source="storages.name")
#     pictures = PictureSerializer(many=True, read_only=True)
#     amount = serializers.IntegerField()

#     class Meta:
#         model = Product
#         fields = "__all__"
#         extra_kwargs = {
#             "available": {"required": True},
#             "barcode": {"required": True},
#             "group_id": {"required": True},
#             "price": {"required": True},
#             "shelf_id": {"required": True},
#             "free_description": {"required": True},
#             "modified_date": {"required": True},
#             "measurements": {"required": True},
#             "weight": {"required": True},
#             "category": {"required": True},
#             "storages": {"required": True},
#             "color": {"required": True},
#         }


# class ProductStorageListSerializer(serializers.ModelSerializer):
#     category_name = serializers.ReadOnlyField(source="category.name")
#     color_name = serializers.ReadOnlyField(source="color.name")
#     storage_name = serializers.ReadOnlyField(source="storages.name")
#     pictures = PictureSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = "__all__"
#         extra_kwargs = {
#             "available": {"required": True},
#             "barcode": {"required": True},
#             "group_id": {"required": True},
#             "price": {"required": True},
#             "shelf_id": {"required": True},
#             "free_description": {"required": True},
#             "modified_date": {"required": True},
#             "measurements": {"required": True},
#             "weight": {"required": True},
#             "category": {"required": True},
#             "storages": {"required": True},
#             "color": {"required": True},
#         }


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


# class ProductCreateSerializer(serializers.ModelSerializer):
#     amount = serializers.IntegerField()
#     pictures = serializers.FileField()
#     color = serializers.IntegerField()

#     class Meta:
#         model = Product
#         fields = "__all__"
#         extra_kwargs = {
#             "available": {"required": True},
#             "barcode": {"required": True},
#             "category": {"required": True},
#             "storages": {"required": True},
#             "color": {"required": True},
#         }


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


class StorageSchemaResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "address": {"required": True},
            "in_use": {"required": True},
        }


class ShoppingCartAvailableAmountListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
