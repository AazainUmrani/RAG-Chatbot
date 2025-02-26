from rest_framework import serializers

class ChatSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)