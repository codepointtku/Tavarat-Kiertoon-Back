from rest_framework import serializers

from .models import Bulletin


class BulletinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bulletin
        fields = "__all__"


class BulletinResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bulletin
        fields = "__all__"
        extra_kwargs = {"author": {"required": True}}
