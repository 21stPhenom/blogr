import jwt

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from config import settings
from config.responses import api_response
from config.utils import generate_otp, otp_exists, send_otp_mail
from apps.accounts.models import CustomUser
from apps.accounts.v1.serializers import inputs, outputs


class Register(APIView):
    model = CustomUser
    serializer_class = inputs.CustomUserSerializer

    @extend_schema(
        responses={201: outputs.UserResponse, 400: outputs.ApiResponse},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(status.HTTP_201_CREATED, message="user created", data=serializer.data)


class Login(APIView):
    model = CustomUser
    serializer_class = inputs.LoginSerializer

    @extend_schema(responses={200: outputs.LoginResponse, 400: outputs.ApiResponse})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email, password = serializer.data.values()
        username = get_object_or_404(self.model, email=email).username
        user = authenticate(request, username=username, password=password)

        if user is None:
            return api_response(status.HTTP_404_NOT_FOUND, message="no user found")

        token = jwt.encode(
            {
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            key=settings.SECRET_KEY,
        )
        user_serializer = inputs.CustomUserSerializer(user)
        return api_response(
            status.HTTP_200_OK,
            message="login successful",
            data={"user": user_serializer.data, "token": token},
        )


class ForgotPassword(APIView):
    model = CustomUser
    serializer_class = inputs.ForgotPasswordSerializer

    @extend_schema(
        responses={200: outputs.ApiResponse, 400: outputs.ApiResponse}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(self.model, email=serializer.data["email"])
        otp = generate_otp(user)

        mail_response = send_otp_mail(otp, user.email)
        if mail_response == "sent":
            return api_response(status.HTTP_200_OK, message="email sent")
        elif mail_response == "error":
            return api_response(status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPassword(APIView):
    model = CustomUser
    serializer_class = inputs.ResetPasswordSerializer

    @extend_schema(
        responses={200: outputs.ApiResponse, 400: outputs.ApiResponse}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(self.model, serializer.data["email"])
        otp_is_valid = otp_exists(user, serializer.data["otp"])

        if otp_is_valid is True:
            user.set_password(serializer.data["new_password"])
            user.save()
            return api_response(
                status.HTTP_200_OK, message="password reset successfully"
            )

        else:
            return api_response(
                status.HTTP_400_BAD_REQUEST, message="invalid otp", data=serializer.data
            )


class Account(APIView):
    model = CustomUser
    serializer_class = inputs.CustomUserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: outputs.UserResponse, 400: outputs.ApiResponse},
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)

        return api_response(status.HTTP_200_OK, message="success", data=serializer.data)

    @extend_schema(
        responses={200: outputs.UserResponse, 400: outputs.ApiResponse},
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(
            instace=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = inputs.CustomUserSerializer(user)

        return api_response(
            status.HTTP_200_OK, message="account updated", data=user.data
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return api_response(status.HTTP_204_NO_CONTENT, message="account deleted")


class Follow(APIView):
    model = CustomUser
    permission_classes = [IsAuthenticated]
    serializer_class = inputs.CustomUserSerializer

    @extend_schema(
        responses={200: outputs.UserResponse, 400: outputs.ApiResponse},
    )
    def get(self, request, username, *args, **kwargs):
        current_user: CustomUser = request.user
        if current_user.username == username:
            message = "can't follow self"
            return api_response(status.HTTP_400_BAD_REQUEST, message=message)

        target_user = get_object_or_404(self.model, username=username)
        if target_user in current_user.following.all():
            message = "already following user"
            return api_response(status.HTTP_400_BAD_REQUEST, message=message)

        target_user.followers.add(current_user)
        current_user.following.add(target_user)

        serializer = inputs.CustomUserSerializer(current_user)

        message = "followed successfully"
        return api_response(status.HTTP_200_OK, message=message, data=serializer.data)


class Unfollow(APIView):
    model = CustomUser
    permission_classes = [IsAuthenticated]
    serializer_class = inputs.CustomUserSerializer

    @extend_schema(
        responses={200: outputs.UserResponse, 400: outputs.ApiResponse},
    )
    def get(self, request, username, *args, **kwargs):
        current_user: CustomUser = request.user

        if current_user.username == username:
            message = "can't unfollow self"
            return api_response(status.HTTP_400_BAD_REQUEST, message)

        target_user = get_object_or_404(self.model, username=username)
        if not target_user in current_user.following.all():
            message = "not following user"
            return api_response(status.HTTP_400_BAD_REQUEST, message=message)

        target_user.followers.remove(current_user)
        current_user.following.remove(current_user)

        serializer = inputs.CustomUserSerializer(current_user)
        message = "unfollowed successfully"

        return api_response(status.HTTP_200_OK, message=message, data=serializer.data)
