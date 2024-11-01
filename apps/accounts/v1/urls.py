from django.urls import path

from apps.accounts.v1 import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.Register.as_view(), name="register"),
    path("login/", views.Login.as_view(), name="login"),
    path("forgot-password/", views.ForgotPassword.as_view(), name="forgot_password"),
    path("reset-password/", views.ResetPassword.as_view(), name="reset-password"),
    path("account/", views.Account.as_view(), name="account"),
    path("follow/<str:username>/", views.Follow.as_view(), name="follow"),
    path("unfollow/<str:username>/", views.Unfollow.as_view(), name="unfollow")
]
