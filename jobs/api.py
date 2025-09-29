# jobs/api.py
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer
from .permissions import (
    IsRecruiter, IsSeeker, IsJobOwner, IsApplicationOwnerOrRecruiter
)
from accounts.models import Roles

User = get_user_model()


class JobViewSet(viewsets.ModelViewSet):
    """
    ניהול משרות.
    - list/retrieve: פתוח לכל (אפשר לשנות ל-IsAuthenticated אם תרצי)
    - create/update/destroy: רק RECRUITER ובעל המשרה.
    """
    queryset = Job.objects.all().select_related("posted_by")
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action in ["create"]:
            # משתמש מחובר וגם מגייס
            return [permissions.IsAuthenticated(), IsRecruiter()]
        if self.action in ["update", "partial_update", "destroy"]:
            # מחובר, מגייס, וגם בעל המשרה (בדיקת אובייקט)
            return [permissions.IsAuthenticated(), IsRecruiter(), IsJobOwner()]
        # ברירת מחדל – מחייב התחברות
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # posted_by יוגדר למשתמש המחובר; ה-serializer גם מגדיר זאת, אבל נשמור עקביות
        if self.request.user.role != Roles.RECRUITER:
            raise PermissionDenied("רק מגייס יכול לפרסם משרה.")
        serializer.save(posted_by=self.request.user)

    # ב-update/destroy בדיקת בעלות תתבצע ע״י IsJobOwner.has_object_permission


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ניהול הגשות למשרות.
    - create: רק SEEKER
    - list/retrieve/update/destroy: מחייב התחברות.
      * SEEKER רואה/מנהל רק את ההגשות שלו.
      * RECRUITER רואה את ההגשות למשרות שהוא פרסם.
    """
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # אין חשיפת רשימות הגשות למשתמשים לא מחוברים
            return Application.objects.none()

        base_qs = Application.objects.select_related("job", "applicant", "job__posted_by")

        if user.role == Roles.SEEKER:
            return base_qs.filter(applicant=user)
        if user.role == Roles.RECRUITER:
            return base_qs.filter(job__posted_by=user)
        return Application.objects.none()

    def get_permissions(self):
        if self.action == "create":
            # חייב להיות מחפש עבודה
            return [permissions.IsAuthenticated(), IsSeeker()]
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            # חייב להיות מחובר וגם לעמוד בהרשאת אובייקט
            return [permissions.IsAuthenticated(), IsApplicationOwnerOrRecruiter()]
        # list – מחייב התחברות (יסנן לפי תפקיד ב-get_queryset)
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # applicant יוגדר למשתמש המחובר
        if self.request.user.role != Roles.SEEKER:
            raise PermissionDenied("רק מחפש עבודה יכול להגיש מועמדות.")
        serializer.save(applicant=self.request.user)
