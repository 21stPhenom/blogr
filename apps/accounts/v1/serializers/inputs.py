from rest_framework import serializers

from apps.accounts.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    
    following = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username"
    )
    
    followers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username"
    )
    
    class Meta:
        model = CustomUser
        fields = "__all__"
        read_only_fields = [
            "followers",
            "following",
            "groups",
            "date_joined",
            "user_permissions",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active"
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "bio": {"required": False},
        }

    def create(self, validated_data, *args, **kwargs):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField()
    new_password = serializers.CharField()
