from rest_framework import serializers

from .models import Bike


class BikeSerializer(serializers.ModelSerializer):
    type_name = serializers.ReadOnlyField(source="type.name")
    brand_name = serializers.ReadOnlyField(source="brand.name")
    size_name = serializers.ReadOnlyField(source="size.name")
    color_name = serializers.ReadOnlyField(source="color.name")

    class Meta:
        model = Bike
        fields = "__all__"
