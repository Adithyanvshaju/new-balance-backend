
from rest_framework import serializers
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AdminLoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        data = super().validate(attrs)

        if not self.user.is_staff:
            raise serializers.ValidationError(
                "You are not authorized to access the admin panel."
            )

        data['username'] = self.user.username
        data['is_staff'] = self.user.is_staff

        return data


class AdminUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'is_active',
            'date_joined'
        ]

