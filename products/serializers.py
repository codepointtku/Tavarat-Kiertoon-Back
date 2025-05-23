from rest_framework import serializers

from .models import Color, Picture, Product, ProductItem, ProductItemLogEntry, Storage
from categories.models import Category


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


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"


class StorageResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "address": {"required": True},
            "in_use": {"required": True},
        }


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"
        read_only_fields = ["default"]


class ProductSerializer(serializers.ModelSerializer):
    pictures = PictureSerializer(many=True, read_only=True)
    amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    colors = ColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def get_amount(self, obj) -> int:
        product_amount = ProductItem.objects.filter(
            product=obj.id, available=True
        ).count()
        return product_amount

    def get_category_name(self, obj) -> str:
        return obj.category_name

    def get_total_amount(self, obj) -> int:
        total_product_amount = ProductItem.objects.filter(product=obj.id).count()
        return total_product_amount


class ProductDetailSerializer(serializers.ModelSerializer):
    product_items = serializers.SerializerMethodField()
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

    def get_product_items(self, obj):
        qs = obj.productitem_set.all()
        serializer = ProductItemStorageSerializer(qs, read_only=True, many=True)
        return serializer.data


class ProductResponseSerializer(ProductSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "price": {"required": True},
            "free_description": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},
            "category": {"required": True},
            "colors": {"required": True},
        }


class ProductItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        exclude = ["modified_date", "product", "log_entries"]
        extra_kwargs = {
            "available": {"required": True},
            "barcode": {"required": True},
            "storage": {"required": True},
        }


class ProductCreateSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    available = serializers.BooleanField()
    barcode = serializers.CharField()
    storage = serializers.IntegerField()
    shelf_id = serializers.CharField(required=False)

    class Meta:
        model = Product
        exclude = ["pictures", "colors"]

    def create(self, validated_data):
        amount = validated_data.pop("amount")

        product_item = {}
        product_item["available"] = validated_data.pop("available")
        product_item["barcode"] = validated_data.pop("barcode")
        product_item["storage"] = validated_data.pop("storage")
        if "shelf_id" in validated_data:
            product_item["shelf_id"] = validated_data.pop("shelf_id")
        product_item_serializer = ProductItemCreateSerializer(data=product_item)
        product_item_serializer.is_valid(raise_exception=True)

        product = Product.objects.create(**validated_data)
        log_entry = ProductItemLogEntry.objects.create(
            action=ProductItemLogEntry.ActionChoices.CREATE, user=self.context
        )
        for _ in range(amount):
            pi = ProductItem.objects.create(
                product=product, **product_item_serializer.validated_data
            )
            pi.log_entries.add(log_entry)
        return product


class ProductCreateRequestSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    available = serializers.BooleanField()
    barcode = serializers.CharField()
    storage = serializers.IntegerField()
    shelf_id = serializers.CharField(required=False)
    pictures = serializers.ListField(required=False)

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "amount": {"required": True},
            "category": {"required": True},
            "colors": {"required": False},
        }


class ProductUpdateSerializer(serializers.ModelSerializer):
    new_pictures = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    old_pictures = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    shelf_id = serializers.CharField(required=False)
    storage = serializers.IntegerField(required=False)
    barcode = serializers.CharField(required=False)

    class Meta:
        model = Product
        exclude = ["pictures"]
        extra_kwargs = {
            "name": {"required": True},
            "category": {"required": True},
        }


class ProductUpdateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "category": {"required": True},
            "colors": {"required": True},
            "pictures": {"required": True},
            "price": {"required": True},
            "free_description": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},
        }


class ProductStorageTransferSerializer(serializers.Serializer):
    storage = serializers.IntegerField()
    product_items = serializers.ListField(child=serializers.IntegerField())


class ShoppingCartAvailableAmountListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class ProductItemLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItemLogEntry
        fields = "__all__"


class ProductItemLogEntryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItemLogEntry
        fields = "__all__"
        extra_kwargs = {"action": {"required": True}, "user": {"required": True}}


class ProductItemSerializer(serializers.ModelSerializer):
    """
    serializer for product items, for listing purposes
    """

    product = ProductSerializer(read_only=True)
    storage = StorageSerializer(read_only=True)
    log_entries = ProductItemLogEntrySerializer(read_only=True, many=True)

    class Meta:
        model = ProductItem
        fields = "__all__"


class ProductItemStorageSerializer(serializers.ModelSerializer):
    """
    serializer for ProductStorageSerializer
    """

    storage = StorageSerializer(read_only=True)
    log_entries = ProductItemLogEntryResponseSerializer(read_only=True, many=True)

    class Meta:
        model = ProductItem
        exclude = ["product"]
        extra_kwargs = {
            "available": {"required": True},
            "modified_date": {"required": True},
            "shelf_id": {"required": True},
            "barcode": {"required": True},
        }


class ProductDetailResponseSerializer(ProductSerializer):
    product_items = ProductItemStorageSerializer(
        source="get_product_items", read_only=True, many=True
    )
    colors = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "price": {"required": True},
            "free_description": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},
            "category": {"required": True},
            "colors": {"required": True},
        }

    def get_product_items(self, obj):
        return obj.productitem_set.all()


class ProductStorageSerializer(serializers.ModelSerializer):
    product_items = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField()
    amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_product_items(self, obj):
        qs = obj.productitem_set.all()
        serializer = ProductItemStorageSerializer(qs, read_only=True, many=True)
        return serializer.data

    def get_amount(self, obj) -> int:
        product_amount = ProductItem.objects.filter(
            product=obj.id, available=True
        ).count()
        return product_amount

    def get_total_amount(self, obj) -> int:
        total_product_amount = ProductItem.objects.filter(product=obj.id).count()
        return total_product_amount


class ProductStorageResponseSerializer(serializers.ModelSerializer):
    product_items = ProductItemStorageSerializer(
        source="get_product_items", read_only=True, many=True
    )
    category_name = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "price": {"required": True},
            "free_description": {"required": True},
            "measurements": {"required": True},
            "weight": {"required": True},
            "category": {"required": True},
            "pictures": {"required": True},
            "colors": {"required": True},
        }

    def get_product_items(self, obj):
        return obj.productitem_set.all()


class ProductItemResponseSerializer(serializers.ModelSerializer):
    product = ProductResponseSerializer(read_only=True)
    storage = StorageResponseSerializer(read_only=True)
    log_entries = ProductItemLogEntryResponseSerializer(read_only=True, many=True)

    class Meta:
        model = ProductItem
        fields = "__all__"
        extra_kwargs = {
            "available": {"required": True},
            "modified_date": {"required": True},
            "shelf_id": {"required": True},
            "barcode": {"required": True},
            "log_entries": {"required": True},
        }


class ProductItemUpdateSerializer(serializers.ModelSerializer):
    """
    serializer for product items for purpose of updating it.
    """

    modify_date = serializers.CharField(required=False)

    class Meta:
        model = ProductItem
        fields = "__all__"
        read_only_fields = ["product", "modified_date", "log_entries"]


class ProductItemDetailResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = "__all__"
        extra_kwargs = {
            "available": {"required": True},
            "modified_date": {"required": True},
            "shelf_id": {"required": True},
            "barcode": {"required": True},
            "product": {"required": True},
            "storage": {"required": True},
            "log_entries": {"required": True},
        }


class ReturnAddProductItemsSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)

    class Meta:
        fields = "amount"
