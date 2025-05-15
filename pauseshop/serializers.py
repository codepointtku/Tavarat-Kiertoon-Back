from .models import Pause
from rest_framework import serializers


class PauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pause
        fields = "__all__"
