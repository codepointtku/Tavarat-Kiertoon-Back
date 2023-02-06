from rest_framework import serializers

from .models import Bulletin, BulletinSubject


class BulletinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bulletin
        fields = "__all__"


class BulletinSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletinSubject
        fields = "__all__"
