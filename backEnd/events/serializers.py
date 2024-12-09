from rest_framework import serializers
from .views import  Event
class EventSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='branch.city', read_only=True)
    participant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = ['id','date', 'description', 'branch', 'city', 'created_by','participant_count']
