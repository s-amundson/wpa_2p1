from rest_framework import serializers
from ..models import StudentFamily


class StudentFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFamily
        fields = ['street', 'street', 'state', 'post_code', 'phone']
