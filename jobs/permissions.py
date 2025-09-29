# jobs/permissions.py
from rest_framework.permissions import BasePermission
from accounts.models import Roles


class IsRecruiter(BasePermission):
    """מאפשר רק למגייסים לפרסם/לערוך משרות"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.RECRUITER


class IsSeeker(BasePermission):
    """מאפשר רק למחפשי עבודה להגיש מועמדות"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Roles.SEEKER


class IsJobOwner(BasePermission):
    """מאפשר למגייס לנהל רק משרות שהוא עצמו פרסם"""
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.posted_by == request.user


class IsApplicationOwnerOrRecruiter(BasePermission):
    """
    למחפש עבודה → רואה/עורך רק את ההגשות שלו.
    למגייס → רואה את כל ההגשות למשרות שהוא פרסם.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == Roles.SEEKER:
            return obj.applicant == request.user
        if request.user.role == Roles.RECRUITER:
            return obj.job.posted_by == request.user
        return False
