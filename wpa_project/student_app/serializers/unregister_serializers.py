from rest_framework import serializers


class UnregisterSerializer(serializers.Serializer):
    class_list = serializers.ListField(required=True)
