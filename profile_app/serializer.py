from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "is_active"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer("user")

    class Meta:
        model = Profile
        fields = ["id", "user"]

