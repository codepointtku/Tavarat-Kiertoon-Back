from rest_framework import serializers

from .models import Bike, BikeAmount, BikePackage, BikeRental, BikeStock


class BikeRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeRental
        fields = [
            "id",
            "start_date",
            "end_date",
        ]


class BikeStockSerializer(serializers.ModelSerializer):
    rental = BikeRentalSerializer(many=True)

    class Meta:
        model = BikeStock
        fields = [
            "id",
            "number",
            "frame_number",
            "created_at",
            "state",
            "storage",
            "rental",
        ]


class BikeSerializer(serializers.ModelSerializer):
    # color = serializers.StringRelatedField(many=True)
    type_name = serializers.ReadOnlyField(source="type.name")
    brand_name = serializers.ReadOnlyField(source="brand.name")
    size_name = serializers.ReadOnlyField(source="size.name")
    color_name = serializers.ReadOnlyField(source="color.name")
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
            "type_name",
            "brand_name",
            "size_name",
            "color_name",
        ]


class BikeAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BikeAmount
        fields = ["bike", "amount"]


class BikePackageSerializer(serializers.ModelSerializer):
    # bikes = serializers.StringRelatedField(many=True)
    bikes = BikeAmountSerializer(many=True)

    class Meta:
        model = BikePackage
        fields = [
            "id",
            "name",
            "description",
            "bikes",
        ]
