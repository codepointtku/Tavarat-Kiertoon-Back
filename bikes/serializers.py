from rest_framework import serializers

from .models import Bike, BikePackage


class BikeSerializer(serializers.ModelSerializer):
    # color = serializers.StringRelatedField(many=True)
    type_name = serializers.ReadOnlyField(source="type.name")
    brand_name = serializers.ReadOnlyField(source="brand.name")
    size_name = serializers.ReadOnlyField(source="size.name")
    color_name = serializers.ReadOnlyField(source="color.name")
    max_available = serializers.ReadOnlyField(source="stock.count")

    class Meta:
        model = Bike
        fields = [
            "id",
            "name",
            "max_available",
            "stock",
            "description",
            "type_name",
            "brand_name",
            "size_name",
            "color_name",
        ]


class BikePackageSerializer(serializers.ModelSerializer):
    bikes = serializers.StringRelatedField(many=True)

    class Meta:
        model = BikePackage
        fields = [
            "id",
            "name",
            "description",
            "bikes",
        ]
