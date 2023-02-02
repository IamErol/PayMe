from rest_framework import serializers


# .data serialized data

class SubscribeSerializer(serializers.Serializer):
    # id = serializers.IntegerField(read_only=True)
    params = serializers.JSONField(read_only=True)  #validates if data in json format