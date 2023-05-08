from rest_framework import serializers

from .models import (
    Bike,
    BikeAmount,
    BikePackage,
    BikeRental,
    BikeStock,
    BikeType,
    BikeSize,
    BikeBrand,
)

from products.serializers import ColorSerializer, StorageSerializer


class BikeRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeRental
        fields = "__all__"


class BikeRentalSchemaPostSerializer(serializers.ModelSerializer):
    bike_stock = serializers.DictField(child=serializers.IntegerField())

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
        fields = ["bike", "amount", "id"]


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

    def create(self, validated_data):
        bikemodels_data = validated_data.pop("bikes")

        package = BikePackage.objects.create(**validated_data)

        for bikemodel_data in bikemodels_data:
            BikeAmount.objects.create(package=package, **bikemodel_data)
        return package
    
    def update(self, instance, validated_data):
        bikemodels_data = validated_data.pop("bikes")

        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        bikeamount_ids = BikeAmount.objects.filter(package_id=instance.pk).values_list('id', flat=True)
        print(bikeamount_ids)
        bikeamount_set = []

        for bikemodel_data in bikemodels_data:
            if "id" in bikemodel_data.keys():
                if BikeAmount.objects.filter(id=bikemodel_data['id']).exists():
                    bikeamount_instance = BikeAmount.objects.get(id=bikemodel_data['id'])
                    bikeamount_instance.amount = bikemodel_data.get('amount', bikeamount_instance.amount)
                    bikeamount_instance.bike = bikemodel_data.get('bike', bikeamount_instance.bike)
                    bikeamount_instance.save()
                    bikeamount_set.append(bikeamount_instance.id)
                else:
                    continue
            else:
                bikeamount_instance = BikeAmount.objects.create(package=instance, **bikemodel_data)
                bikeamount_set.append(bikeamount_instance.id)

        for bikeamount_id in bikeamount_ids:
            if bikeamount_id not in bikeamount_set:
                BikeAmount.objects.filter(pk=bikeamount_id).delete()

        return instance


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
        fields = "__all__"


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
    unavailable = serializers.DictField(child=serializers.IntegerField())
    package_only_count = serializers.IntegerField()
    package_only_unavailable = serializers.DictField(child=serializers.IntegerField())


class MainBikeSchemaPackageBikeSerializer(serializers.Serializer):
    bike = serializers.IntegerField()
    amount = serializers.IntegerField()


class MainBikeSchemaPackageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    bikes = MainBikeSchemaPackageBikeSerializer(many=True)
    type = serializers.CharField()
    unavailable = serializers.DictField(child=serializers.IntegerField())
    brand = serializers.IntegerField()
    color = serializers.IntegerField()
    size = serializers.CharField()
    max_available = serializers.IntegerField()


class MainBikeListSchemaSerializer(serializers.Serializer):
    date_info = MainBikeSchemaDateSerializer()
    bikes = MainBikeSchemaBikesSerializer(many=True)
    packages = MainBikeSchemaPackageSerializer(many=True)


class BikeAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeAmount
        fields = "__all__"

