from rest_framework import permissions
from django.contrib.auth import get_user_model
from .enums import RoleEnum


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to super admin users. """
    message = "Only Super Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and RoleEnum.SuperAdmin.value == request.user.roles)


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users. """
    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and RoleEnum.Admin.value == request.user.role)


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """Allows access only to admin and SuperAdmin users. """
    message = "Only Admins and super Admins are authorized to perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and (
                RoleEnum.Admin.value == request.user.role or RoleEnum.SuperAdmin.value == request.user.role))
