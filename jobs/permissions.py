# jobs/permissions.py
from rest_framework.permissions import BasePermission
from accounts.models import Roles


class IsRecruiter(BasePermission):
    """
    מאפשר רק למגייסים לפרסם או לערוך משרות.
    Admin (is_staff/superuser) מקבל גישה מלאה.
    """

    @staticmethod
    def _is_admin(u):
        return getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == Roles.RECRUITER or self._is_admin(request.user)
        )


class IsSeeker(BasePermission):
    """
    מאפשר רק למחפשי עבודה להגיש מועמדות.
    Admin (is_staff/superuser) מקבל גישה מלאה.
    """

    @staticmethod
    def _is_admin(u):
        return getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == Roles.SEEKER or self._is_admin(request.user)
        )


class IsJobOwner(BasePermission):
    """
    מאפשר למגייס לנהל רק משרות שהוא עצמו פרסם.
    Admin מקבל גישה לכל המשרות.
    """

    @staticmethod
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
    Admin → יכול לגשת לכול.
    """

    @staticmethod
    def _is_admin(u):
        return getattr(u, "is_staff", False) or getattr(u, "is_superuser", False)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == Roles.SEEKER:
            return obj.applicant == user or self._is_admin(user)

        if user.role == Roles.RECRUITER:
            return obj.job.posted_by == user or self._is_admin(user)

        return self._is_admin(user)
