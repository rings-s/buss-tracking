from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import authenticate
from django.utils import timezone

import requests
from django.conf import settings

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)


# =============================================================================
# JWT TOKEN UTILITIES
# =============================================================================

def get_tokens_for_user(user):
    """Generate JWT tokens for a user with custom claims"""
    refresh = RefreshToken.for_user(user)

    # Add custom claims
    refresh['role'] = user.role
    refresh['email'] = user.email
    refresh['full_name'] = user.full_name

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

class LoginAPIView(APIView):
    """
    User login endpoint
    POST /api/auth/login/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_user(user)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data,
        })


class LogoutAPIView(APIView):
    """
    User logout - blacklists refresh token
    POST /api/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({'message': 'Logout successful'})
        except TokenError:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TokenRefreshAPIView(APIView):
    """
    Refresh access token
    POST /api/auth/token/refresh/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        except TokenError:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


# =============================================================================
# REGISTRATION VIEWS
# =============================================================================

class RegisterAPIView(APIView):
    """
    User registration endpoint
    POST /api/auth/register/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegisterAPIView(APIView):
    """
    Admin-only user registration (can create drivers/admins)
    POST /api/auth/admin/register/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserRegistrationSerializer(
            data=request.data,
            context={'is_admin': True}
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': f'{user.role.capitalize()} created successfully'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# GOOGLE OAUTH VIEWS
# =============================================================================

class GoogleLoginView(APIView):
    """
    Google OAuth2 login endpoint
    POST /api/auth/google/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')

        if not code:
            return Response(
                {'error': 'Authorization code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Exchange code for tokens
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
            'client_secret': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
            'redirect_uri': 'http://localhost:5173/auth/google/callback',
            'grant_type': 'authorization_code',
        }

        token_response = requests.post(token_url, data=token_data)

        if token_response.status_code != 200:
            return Response(
                {'error': 'Failed to exchange code for tokens'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token_json = token_response.json()
        access_token = token_json.get('access_token')

        # Get user info from Google
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        userinfo_response = requests.get(
            userinfo_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if userinfo_response.status_code != 200:
            return Response(
                {'error': 'Failed to get user info from Google'},
                status=status.HTTP_400_BAD_REQUEST
            )

        userinfo = userinfo_response.json()
        email = userinfo.get('email')
        full_name = userinfo.get('name', '')

        if not email:
            return Response(
                {'error': 'Email not provided by Google'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email.lower(),
            defaults={
                'full_name': full_name,
                'role': 'employee',
                'is_active': True,
            }
        )

        if not created and not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data,
        })


# =============================================================================
# USER PROFILE VIEWS
# =============================================================================

class UserProfileAPIView(APIView):
    """
    Get/Update current user profile
    GET/PUT/PATCH /api/auth/user/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=False
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Profile updated successfully'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Profile updated successfully'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    """
    Change user password
    POST /api/auth/password/change/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            tokens = get_tokens_for_user(user)

            return Response({
                'tokens': tokens,
                'message': 'Password changed successfully'
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# UTILITY VIEWS
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    """Verify if token is valid"""
    return Response({
        'valid': True,
        'user': UserSerializer(request.user).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_users_by_role(request):
    """Get users filtered by role (admin only)"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    role = request.query_params.get('role')
    users = User.objects.filter(role=role, is_active=True) if role else User.objects.filter(is_active=True)

    serializer = UserSerializer(users, many=True)
    return Response({'users': serializer.data, 'count': users.count()})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_nfc_uid(request):
    """Assign NFC UID to employee (admin only)"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    user_id = request.data.get('user_id')
    nfc_uid = request.data.get('nfc_uid')

    if not user_id or not nfc_uid:
        return Response(
            {'error': 'user_id and nfc_uid are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(id=user_id, role='employee')
    except User.DoesNotExist:
        return Response(
            {'error': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if User.objects.filter(nfc_uid=nfc_uid).exclude(id=user_id).exists():
        return Response(
            {'error': 'NFC UID already assigned to another user'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.nfc_uid = nfc_uid
    user.save(update_fields=['nfc_uid'])

    return Response({
        'user': UserSerializer(user).data,
        'message': 'NFC UID assigned successfully'
    })
