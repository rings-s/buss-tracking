from django.urls import path, include
from .views import (
    LoginAPIView,
    LogoutAPIView,
    TokenRefreshAPIView,
    RegisterAPIView,
    AdminRegisterAPIView,
    GoogleLoginView,
    UserProfileAPIView,
    ChangePasswordAPIView,
    verify_token,
    get_users_by_role,
    assign_nfc_uid,
)

urlpatterns = [
    # Authentication
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshAPIView.as_view(), name='token-refresh'),
    path('verify/', verify_token, name='verify-token'),

    # Registration
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('admin/register/', AdminRegisterAPIView.as_view(), name='admin-register'),

    # Google OAuth
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    path('google/callback/', include('allauth.socialaccount.providers.google.urls')),

    # User Profile
    path('user/', UserProfileAPIView.as_view(), name='user-profile'),
    path('password/change/', ChangePasswordAPIView.as_view(), name='change-password'),

    # Admin Utilities
    path('users/', get_users_by_role, name='users-by-role'),
    path('assign-nfc/', assign_nfc_uid, name='assign-nfc'),
]
