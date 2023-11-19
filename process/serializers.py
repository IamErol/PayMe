from rest_framework import serializers


class SubscribeSerializer(serializers.Serializer):
    params = serializers.JSONField()
