from rest_framework import serializers
from user.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("Username cannot be empty")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists")
        return value
    
    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password cannot be empty")
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase character")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase character")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            pswd=validated_data['password']
        )
        return user
