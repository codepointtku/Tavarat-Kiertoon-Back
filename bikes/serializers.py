from rest_framework import serializers

from .models import Bike, BikeAmount, BikePackage, BikeRental, BikeStock, BikeType, BikeSize, BikeBrand

from products.serializers import ColorSerializer, StorageSerializer


class BikeRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeRental
        fields = "__all__"


class BikeRentalSchemaPostSerializer(serializers.ModelSerializer):
    bike_stock = serializers.DictField()

    class Meta:
        model = BikeRental
        fields = "__all__"


class BikeStockSerializer(serializers.ModelSerializer):
    rental = BikeRentalSerializer(many=True)

    class Meta:
        model = BikeStock
        fields = [
            "id",
            "bike",
            "number",
            "frame_number",
            "created_at",
            "state",
            "package_only",
            "storage",
            "rental",
        ]


class BikeSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField(source="type.name")
    brand = serializers.StringRelatedField(source="brand.name")
    size = serializers.StringRelatedField(source="size.name")
    color = serializers.StringRelatedField(source="color.name")
    max_available = serializers.ReadOnlyField(source="stock.count")

    # bikes = serializers.StringRelatedField(many=True)
    stock = BikeStockSerializer(many=True)

    class Meta:
        model = Bike
        fields = [
            "id",
            "name",
            "max_available",
            "stock",
            "description",
            "type",
            "brand",
            "size",
            "color",
        ]


class BikeAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeAmount
        fields = ["bike", "amount"]


class BikePackageSerializer(serializers.ModelSerializer):
    bikes = BikeAmountSerializer(many=True)

    class Meta:
        model = BikePackage
        fields = [
            "id",
            "name",
            "description",
            "bikes",
        ]


class BikeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeType
        fields = "__all__"


class BikeBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeBrand
        fields = "__all__"


class BikeSizeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BikeSize
        fields = "__all__"


class BikeStockDepthSerializer(serializers.ModelSerializer):
    type = BikeTypeSerializer(read_only=True)
    brand = BikeBrandSerializer(read_only=True)
    size = BikeSizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)

    class Meta:
        model = Bike
        fields = "__all__"


class BikeStockListSerializer(serializers.ModelSerializer):
    bike = BikeStockDepthSerializer(read_only=True)

    class Meta:
        model = BikeStock
        fields =  "__all__"


class BikeStockCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeStock
        fields = "__all__"

        
class BikeStockDetailSerializer(serializers.ModelSerializer):
    bike = BikeStockDepthSerializer(read_only=True)
    storage = StorageSerializer(read_only=True)
    
    class Meta:
        model = BikeStock
        fields = "__all__"


class BikeModelSerializer(serializers.ModelSerializer):
    type = BikeTypeSerializer(read_only=True)
    brand = BikeBrandSerializer(read_only=True)
    size = BikeSizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    
    class Meta:
        model = Bike
        fields = "__all__"


class BikeModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = "__all__"


class MainBikeSchemaDateSerializer(serializers.Serializer):
    available_from = serializers.DateField()
    available_to = serializers.DateField()     


class MainBikeSchemaBikesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    max_available = serializers.IntegerField()
    description = serializers.CharField()
    type = serializers.CharField()
    brand = serializers.CharField()
    size = serializers.CharField()
    color = serializers.IntegerField()
    unavailable = serializers.DictField()
    package_only_count = serializers.IntegerField()
    package_only_unavailable = serializers.DictField()


class MainBikeSchemaPackageBikeSerializer(serializers.Serializer):
    bike = serializers.IntegerField()
    amount = serializers.IntegerField()


class MainBikeSchemaPackageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    bikes = MainBikeSchemaPackageBikeSerializer(many=True)
    type = serializers.CharField()
    unavailable = serializers.DictField()
    brand = serializers.IntegerField()
    color = serializers.IntegerField()
    size = serializers.CharField()
    max_available = serializers.IntegerField()

class MainBikeListSchemaSerializer(serializers.Serializer):
    date_info = MainBikeSchemaDateSerializer()
    bikes = MainBikeSchemaBikesSerializer(many=True)
    packages = MainBikeSchemaPackageSerializer(many=True)

