from rest_framework import serializers
from ..models import StudentFamily


class StudentFamilySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = StudentFamily
        fields = ['id', 'street', 'city', 'state', 'post_code', 'phone']
