from rest_framework import serializers

from products.serializers import (
    ColorSerializer,
    PictureCreateSerializer,
    PictureSerializer,
)
from users.serializers import UserBikeRentalSerializer

from .models import (
    Bike,
    BikeAmount,
    BikeBrand,
    BikePackage,
    BikeRental,
    BikeSize,
    BikeStock,
    BikeTrailer,
    BikeTrailerModel,
    BikeType,
)


class BikeRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeRental
        fields = "__all__"


class BikeRentalSchemaPostSerializer(serializers.ModelSerializer):
    bike_stock = serializers.DictField(child=serializers.IntegerField())
    bike_trailer = serializers.IntegerField(required=False)

    class Meta:
        model = BikeRental
        exclude = ["state", "user"]


class BikeRentalSchemaResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeRental
        fields = "__all__"
        extra_kwargs = {
            "id": {"required": True},
            "start_date": {"required": True},
            "end_date": {"required": True},
            "state": {"required": True},
            "delivery_address": {"required": True},
            "contact_name": {"required": True},
            "contact_phone_number": {"required": True},
            "extra_info": {"required": True},
            "user": {"required": True},
            "bike_stock": {"required": True},
        }


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
            "rental",
        ]


class BikeSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField(source="type.name")
    brand = serializers.StringRelatedField(source="brand.name")
    size = serializers.StringRelatedField(source="size.name")
    color = serializers.StringRelatedField(source="color.name")
    max_available = serializers.SerializerMethodField()
    picture = serializers.StringRelatedField(source="picture.picture_address")

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
            "picture",
        ]

    def get_max_available(self, object):
        available_stock = object.stock.filter(state="AVAILABLE")
        return len(available_stock)


class BikeAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    picture = serializers.StringRelatedField(source="bike.picture.picture_address")

    class Meta:
        model = BikeAmount
        exclude = ["package"]


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

        bikeamount_ids = BikeAmount.objects.filter(package_id=instance.pk).values_list(
            "id", flat=True
        )
        bikeamount_set = []

        for bikemodel_data in bikemodels_data:
            if "id" in bikemodel_data.keys():
                if BikeAmount.objects.filter(id=bikemodel_data["id"]).exists():
                    bikeamount_instance = BikeAmount.objects.get(
                        id=bikemodel_data["id"]
                    )
                    bikeamount_instance.amount = bikemodel_data.get(
                        "amount", bikeamount_instance.amount
                    )
                    bikeamount_instance.bike = bikemodel_data.get(
                        "bike", bikeamount_instance.bike
                    )
                    bikeamount_instance.save()
                    bikeamount_set.append(bikeamount_instance.id)
                else:
                    continue
            else:
                bikeamount_instance = BikeAmount.objects.create(
                    package=instance, **bikemodel_data
                )
                bikeamount_set.append(bikeamount_instance.id)

        for bikeamount_id in bikeamount_ids:
            if bikeamount_id not in bikeamount_set:
                BikeAmount.objects.filter(pk=bikeamount_id).delete()

        return instance


class BikeAmountSchemaResponseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField

    class Meta:
        model = BikeAmount
        exclude = ["package"]
        extra_kwargs = {
            "id": {"required": True},
            "amount": {"required": True},
            "bike": {"required": True},
        }


class BikePackageSchemaResponseSerializer(serializers.ModelSerializer):
    bikes = BikeAmountSchemaResponseSerializer(many=True)

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
    picture = PictureSerializer(read_only=True)

    class Meta:
        model = Bike
        fields = "__all__"


class BikeStockListSerializer(serializers.ModelSerializer):
    bike = BikeStockDepthSerializer(read_only=True)

    class Meta:
        model = BikeStock
        fields = "__all__"
        extra_kwargs = {
            "bike": {"required": True},
            "package_only": {"required": True},
            "number": {"required": True},
            "frame_number": {"required": True},
            "created_at": {"required": True},
            "state": {"required": True},
        }


class BikeStockCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeStock
        fields = "__all__"


class BikeStockDetailSerializer(serializers.ModelSerializer):
    bike = BikeStockDepthSerializer(read_only=True)
    color = ColorSerializer(read_only=True)

    class Meta:
        model = BikeStock
        fields = "__all__"
        extra_kwargs = {
            "bike": {"required": True},
            "package_only": {"required": True},
            "number": {"required": True},
            "frame_number": {"required": True},
            "created_at": {"required": True},
            "state": {"required": True},
        }


class BikeStockSchemaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeStock
        fields = "__all__"
        extra_kwargs = {
            "bike": {"required": True},
            "package_only": {"required": True},
            "number": {"required": True},
            "frame_number": {"required": True},
            "created_at": {"required": True},
            "state": {"required": True},
        }


class BikeModelSerializer(serializers.ModelSerializer):
    type = BikeTypeSerializer(read_only=True)
    brand = BikeBrandSerializer(read_only=True)
    size = BikeSizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    picture = PictureSerializer(read_only=True)

    class Meta:
        model = Bike
        fields = "__all__"


class BikeModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = "__all__"


class BikeModelSchemaResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = "__all__"
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": True},
            "type": {"required": True},
            "brand": {"required": True},
            "size": {"required": True},
            "color": {"required": True},
        }


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
    picture = serializers.CharField()


class MainBikeSchemaPackageBikeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    bike = serializers.IntegerField()
    amount = serializers.IntegerField()
    picture = serializers.CharField()


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
    picture = serializers.CharField()


class MainBikeListSchemaSerializer(serializers.Serializer):
    date_info = MainBikeSchemaDateSerializer()
    bikes = MainBikeSchemaBikesSerializer(many=True)
    packages = MainBikeSchemaPackageSerializer(many=True)


class BikeAmountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeAmount
        fields = "__all__"


class BikeAmountSchemaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeAmount
        exclude = ["package"]


class BikePackageCreateResponseSerializer(serializers.ModelSerializer):
    bikes = BikeAmountSchemaCreateSerializer(many=True)

    class Meta:
        model = BikePackage
        fields = [
            "name",
            "description",
            "bikes",
        ]


class BikeAvailabilityListSerializer(serializers.ModelSerializer):
    rental = BikeRentalSerializer(many=True)

    class Meta:
        model = BikeStock
        fields = [
            "id",
            "rental",
        ]


class BikeTrailerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeTrailerModel
        fields = "__all__"


class BikeTrailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeTrailer
        fields = "__all__"


class BikeTrailerAvailabilityListSerializer(serializers.ModelSerializer):
    trailer_rental = BikeRentalSerializer(many=True)

    class Meta:
        model = BikeTrailer
        fields = [
            "id",
            "trailer_rental",
        ]


class BikeTrailerMainSerializer(serializers.ModelSerializer):
    max_available = serializers.ReadOnlyField(source="trailer.count")
    trailer = BikeTrailerAvailabilityListSerializer(many=True)

    class Meta:
        model = BikeTrailerModel
        fields = [
            "id",
            "name",
            "description",
            "max_available",
            "trailer",
        ]


class BikeRentalDepthSerializer(serializers.ModelSerializer):
    bike_stock = BikeStockDetailSerializer(many=True, read_only=True)
    user = UserBikeRentalSerializer(read_only=True)
    bike_trailer = BikeTrailerSerializer(read_only=True)

    class Meta:
        model = BikeRental
        fields = "__all__"
