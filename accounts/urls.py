from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', views.TokenObtainPairView.as_view(), name='login'),
    path("token/refresh/", TokenRefreshView.as_view(), name='refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify/', views.OTPVerifyView.as_view(), name='verify_otp'),
    path("password/change/", views.PasswordChangeView.as_view(), name='password_change'),
    path("profile/", views.ProfileView.as_view(), name='profile'),
    path("password/reset/request/", views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path("password/reset/verify/", views.PasswordResetVerifyOTP.as_view(), name="password_reset_verify"),
    path("password/reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path('register/edit/email/', views.EditEmailView.as_view(), name='register_edit_email'),
    path('register/edit/phone/', views.EditPhoneView.as_view(), name='register_edit_phone'),
    path("otp/refresh/", views.OTPRefreshView.as_view(), name="otp_refresh"),
]
