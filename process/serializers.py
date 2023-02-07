from rest_framework import serializers


# .data serialized data

class SubscribeSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    params = serializers.JSONField()  #validates if data in json format
    
