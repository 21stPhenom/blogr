from rest_framework import serializers

from apps.accounts.v1.serializers import inputs

class ApiResponse(serializers.Serializer):
    status_code = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.JSONField()

class UserResponse(ApiResponse):
    data = inputs.CustomUserSerializer()
    
class LoginResponse(ApiResponse):
    pass