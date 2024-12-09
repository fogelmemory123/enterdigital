from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'birthday', 'branch']
        extra_kwargs = {
            'password': {'write_only': True}
        }
class UserBirthdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'birthday', 'branch']