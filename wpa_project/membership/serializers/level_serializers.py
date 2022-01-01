from rest_framework import serializers
from ..models import Level


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['name', 'cost', 'description', 'max_age', 'min_age']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
