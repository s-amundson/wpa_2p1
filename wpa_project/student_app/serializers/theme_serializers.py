from rest_framework import serializers


class ThemeSerializer(serializers.Serializer):
    theme = serializers.BooleanField(required=True)
