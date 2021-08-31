from rest_framework import serializers
from ..models import LevelModel


# class MinutesBusinessSerializer(serializers.ModelSerializer):
#     id = serializers.ReadOnlyField()
#     class Meta:
#         model = LevelModel
#         fields = ['id', 'minutes', 'added', 'resolved']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#
# class MinutesReportSerializer(serializers.ModelSerializer):
#     id = serializers.ReadOnlyField()
#     class Meta:
#         model = LevelModel
#         fields = ['id', 'minutes', 'owner', 'report']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
