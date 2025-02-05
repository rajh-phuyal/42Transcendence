from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException

User = get_user_model()

class InternalTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data.update({
            'userId': self.user.id,
            'username': self.user.username,
        })

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['userId'] = user.id
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True) # We will validate it later
    username = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = User
        fields = ('username', 'password')

    def validate_password(self, value):
        if not value:
            raise BarelyAnException(_("Password cannot be empty"))

        if len(value) < 6:
            raise BarelyAnException(_("Password must be at least 6 characters long"))

        if not any(char.islower() for char in value):
            raise BarelyAnException(_("Password must contain at least one lowercase character"))

        if not any(char.isupper() for char in value):
            raise BarelyAnException(_("Password must contain at least one uppercase character"))

        if not any(char.isdigit() for char in value):
            raise BarelyAnException(_("Password must contain at least one digit"))

        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        return user
