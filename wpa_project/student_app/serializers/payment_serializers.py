from rest_framework import serializers


class PaymentSerializer(serializers.Serializer):
    sq_token = serializers.CharField(required=True)
    donation = serializers.FloatField()
