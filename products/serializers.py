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

    def get_amount(self, obj) -> int:
        product_amount = ProductItem.objects.filter(
            product=obj.id, available=True
        ).count()
        return product_amount

    def get_total_amount(self, obj) -> int:
        total_product_amount = ProductItem.objects.filter(product=obj.id).count()
        return total_product_amount


class ProductSchemaResponseSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "price": {"required": True},
            "free_description": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},
            "category": {"required": True},
            "color": {"required": True},
        }


class ProductItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    product_item = ProductItemCreateSerializer()
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
        return product


class ProductItemCreateSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        exclude = ["modified_date", "product"]
        extra_kwargs = {
            "available": {"required": True},
            "barcode": {"required": True},
            "storage": {"required": True},
        }


class ProductCreateSchemaSerializer(serializers.ModelSerializer):
    product_item = ProductItemCreateSchemaSerializer()
    amount = serializers.IntegerField()
    color = serializers.CharField()

    class Meta:
        model = Product
        exclude = ["pictures"]
        extra_kwargs = {
            "name": {"required": True},
            "amount": {"required": True},
            "category": {"required": True},
            "color": {"required": True},
        }


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "category": {"required": True},
            "color": {"required": True},
            "pictures": {"required": True},
        }


class ProductUpdateSchemaResponseSerializer(ProductUpdateSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "category": {"required": True},
            "color": {"required": True},
            "pictures": {"required": True},
            "price": {"required": True},
            "free_description": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},            
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


class ProductItemSerializer(serializers.ModelSerializer):
    """
    serializer for product items, for listing purposes
    """

    product = ProductSerializer(read_only=True)
    storage = StorageSerializer(read_only=True)

    class Meta:
        model = ProductItem
        fields = "__all__"


class ProductItemSchemaResponseSerializer(serializers.ModelSerializer):
    product = ProductSchemaResponseSerializer(read_only=True)
    storage = StorageSchemaResponseSerializer(read_only=True)

    class Meta:
        model = ProductItem
        fields = "__all__"
        extra_kwargs = {
            "available": {"required": True},
            "modified_date": {"required": True},
            "shelf_id": {"required": True},
            "barcode": {"required": True},
        }


class ProductItemUpdateSerializer(serializers.ModelSerializer):
    """
    serializer for product items for purpose of updating it.
    """

    class Meta:
        model = ProductItem
        fields = "__all__"
        extra_kwargs = {
            "modified_date": {"read_only": True},
            "product": {"read_only": True},
        }
