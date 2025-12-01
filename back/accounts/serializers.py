from rest_framework import serializers
from .models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_superuser:
            ret['role'] = 'admin'
        return ret


class UserSerializer(serializers.ModelSerializer):
    """Full user serializer with validation"""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'role', 'is_active', 'nfc_uid', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'nfc_uid': {'required': False, 'allow_null': True},
        }

    def validate_email(self, value):
        """Validate email uniqueness on create/update"""
        instance = getattr(self, 'instance', None)
        if User.objects.filter(email=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_nfc_uid(self, value):
        """Validate NFC UID uniqueness"""
        if value:
            instance = getattr(self, 'instance', None)
            if User.objects.filter(nfc_uid=value).exclude(pk=instance.pk if instance else None).exists():
                raise serializers.ValidationError("NFC UID already registered.")
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_superuser:
            ret['role'] = 'admin'
        return ret


class DriverSerializer(serializers.ModelSerializer):
    """Driver-specific serializer"""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'is_active']
        read_only_fields = fields


class EmployeeSerializer(serializers.ModelSerializer):
    """Employee-specific serializer with NFC info"""
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'nfc_uid', 'is_active']
        read_only_fields = fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer with password validation"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'full_name', 'phone_number', 'role'
        ]
        extra_kwargs = {
            'role': {'required': False},
            'phone_number': {'required': False, 'allow_blank': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value.lower()

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        # Only admin can create admin accounts
        # Drivers and employees can self-register
        role = data.get('role', 'employee')
        is_admin = self.context.get('is_admin', False)

        if role == 'admin' and not is_admin:
            raise serializers.ValidationError({
                'role': 'Only administrators can create admin accounts.'
            })

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'employee')

        user = User.objects.create_user(
            password=password,
            role=role,
            **validated_data
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    DEPRECATED: Use EmployeeProfileSerializer or NonEmployeeProfileSerializer instead.
    Legacy user profile update serializer - kept for backwards compatibility.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'role', 'is_active', 'nfc_uid', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_active', 'created_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_superuser:
            ret['role'] = 'admin'
        return ret


class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Employee profile serializer with NFC card self-registration"""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'role', 'is_active', 'nfc_uid', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_active', 'created_at']

    def validate_nfc_uid(self, value):
        """Validate NFC UID for employees only"""
        if value:
            # Check for duplicates excluding current user
            if User.objects.exclude(id=self.instance.id).filter(nfc_uid=value).exists():
                raise serializers.ValidationError("This NFC card is already registered to another user.")
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_superuser:
            ret['role'] = 'admin'
        return ret


class NonEmployeeProfileSerializer(serializers.ModelSerializer):
    """Admin/Driver profile serializer without NFC card updates"""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'role', 'is_active', 'nfc_uid', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_active', 'created_at', 'nfc_uid']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_superuser:
            ret['role'] = 'admin'
        return ret


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        return data
