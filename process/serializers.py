from rest_framework import serializers


# .data serialized data

class SubscribeSerializer(serializers.Serializer):
    params = serializers.JSONField()  #validates if data in json format
    
