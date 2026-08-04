from rest_framework import permissions
from .models import Application

class IsApplicationCandidate(permissions.BasePermission):
    """
    Разрешает действия только кандидату-авторству заявки
    """
    def has_object_permission(self, request, view, obj):
        return obj.candidate == request.user

class IsApplicationEmployer(permissions.BasePermission):
    """
    Разрешает действия только работодателю, получившему заявку
    """
    def has_object_permission(self, request, view, obj):
        return str(obj.employer_id) == str(request.user.id)

class CanWithdrawApplication(permissions.BasePermission):
    """
    Разрешает отозвать заявку только в определённых статусах
    """
    def has_object_permission(self, request, view, obj):
        if obj.candidate != request.user:
            return False
        return obj.can_withdraw()

class IsApplicationOwner(permissions.BasePermission):
    """
    Разрешает просмотр заявки только кандидату или работодателю
    """
    def has_object_permission(self, request, view, obj):
        return obj.candidate == request.user or str(obj.employer_id) == str(request.user.id)