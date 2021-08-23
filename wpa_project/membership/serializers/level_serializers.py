from rest_framework import serializers
from ..models import LevelModel


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelModel
        fields = ['name', 'cost', 'description', 'max_age', 'min_age']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
