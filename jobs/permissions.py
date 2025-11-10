
from rest_framework.permissions import BasePermission
from accounts.models import Roles


class IsRecruiter(BasePermission):
    """מאפשר רק למגייסים לפרסם או לערוך משרות"""

    def _is_admin(u):
        return getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == Roles.RECRUITER or self._is_admin(request.user)
        )


class IsSeeker(BasePermission):
    """מאפשר רק למחפשי עבודה להגיש מועמדות"""

    def _is_admin(u):
        return getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == Roles.SEEKER or self._is_admin(request.user)
        )


class IsJobOwner(BasePermission):
    """מאפשר למגייס לנהל רק משרות שהוא עצמו פרסם"""

    def _is_admin(u):
        return getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            obj.posted_by == request.user or self._is_admin(request.user)
        )


class IsApplicationOwnerOrRecruiter(BasePermission):
    """
    למחפש עבודה → רואה/עורך רק את ההגשות שלו.
    למגייס → רואה את כל ההגשות למשרות שהוא פרסם.
    """

    def _is_admin(u):
        return getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == Roles.SEEKER:
            return obj.applicant == request.user or self._is_admin(request.user)
        if request.user.role == Roles.RECRUITER:
            return obj.job.posted_by == request.user or self._is_admin(request.user)
        return self._is_admin(request.user)
