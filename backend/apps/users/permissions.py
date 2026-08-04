from rest_framework.permissions import BasePermission

from apps.users.models import UserRole


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == UserRole.STUDENT
        )


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == UserRole.EMPLOYER
        )


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or (
                    hasattr(request.user, 'profile')
                    and request.user.profile.role == UserRole.ADMIN
                )
            )
        )
