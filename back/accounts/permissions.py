from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    message = "Admin access required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsDriver(permissions.BasePermission):
    """Allow access only to driver users"""
    message = "Driver access required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'driver'


class IsEmployee(permissions.BasePermission):
    """Allow access only to employee users"""
    message = "Employee access required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'


class IsAdminOrDriver(permissions.BasePermission):
    """Allow access to admin or driver users"""
    message = "Admin or Driver access required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'driver']


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow full access to admin, read-only to others"""
    message = "Admin access required for this action."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to object owner or admin"""
    message = "You don't have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'driver'):
            return obj.driver == request.user
        if hasattr(obj, 'employee'):
            return obj.employee == request.user
        return False


class CanStartTrip(permissions.BasePermission):
    """Only drivers can start trips"""
    message = "Only drivers can start trips."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'driver'


class CanManageBus(permissions.BasePermission):
    """Admin can manage all, driver can view assigned bus"""
    message = "You don't have permission to manage this bus."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['driver', 'employee']
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.method in permissions.SAFE_METHODS:
            if request.user.role == 'driver':
                return obj.driver == request.user
        return False
