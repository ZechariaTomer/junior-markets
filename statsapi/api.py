from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.models import Roles
from jobs.models import Job, Application


def _last_days(days: int):
    return timezone.now() - timedelta(days=days)


class RecruiterOverviewView(APIView):
    """
    סטטיסטיקות למגייס: ספירת משרות, מועמדויות, חלוקה לפי משרה, וטרנד ל-7 ימים.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, "role", None) != Roles.RECRUITER and not (user.is_staff or user.is_superuser):
            return Response({"detail": "Recruiter only."}, status=status.HTTP_403_FORBIDDEN)

        # סה״כ משרות שפרסם המשתמש
        jobs_qs = Job.objects.filter(posted_by=user)
        jobs_total = jobs_qs.count()

        # סה״כ מועמדויות למשרות שלו
        apps_qs = Application.objects.filter(job__posted_by=user)
        applications_total = apps_qs.count()

        # חלוקת מועמדויות לפי משרה
        applications_by_job = (
            apps_qs.values("job_id", "job__title")
                  .annotate(count=Count("id"))
                  .order_by("-count")
        )

        # טרנד 7 ימים אחרונים (לפי created_at של Application)
        since = _last_days(7)
        last_7d_applications = (
            apps_qs.filter(created_at__gte=since)  # אם שם השדה שונה, עדכני בהתאם
                  .annotate(day=TruncDate("created_at"))
                  .values("day")
                  .annotate(count=Count("id"))
                  .order_by("day")
        )

        data = {
            "jobs_total": jobs_total,
            "applications_total": applications_total,
            "applications_by_job": list(applications_by_job),
            "last_7d_applications": [
                {"date": r["day"], "count": r["count"]} for r in last_7d_applications
            ],
        }
        return Response(data, status=status.HTTP_200_OK)


class SeekerOverviewView(APIView):
    """
    סטטיסטיקות למחפש עבודה: סה״כ הגשות, חלוקה לפי סטטוס, וטרנד 7 ימים.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, "role", None) != Roles.SEEKER and not (user.is_staff or user.is_superuser):
            return Response({"detail": "Seeker only."}, status=status.HTTP_403_FORBIDDEN)

        apps_qs = Application.objects.filter(applicant=user)

        applications_total = apps_qs.count()

        # חלוקה לפי סטטוס
        by_status = (
            apps_qs.values("status")
                   .annotate(count=Count("id"))
                   .order_by("-count")
        )

        # טרנד 7 ימים אחרונים (לפי created_at של Application)
        since = _last_days(7)
        last_7d_submissions = (
            apps_qs.filter(created_at__gte=since)  # אם שם השדה שונה, עדכני בהתאם
                   .annotate(day=TruncDate("created_at"))
                   .values("day")
                   .annotate(count=Count("id"))
                   .order_by("day")
        )

        data = {
            "applications_total": applications_total,
            "by_status": list(by_status),  # [{"status":"PENDING","count":3}, ...]
            "last_7d_submissions": [
                {"date": r["day"], "count": r["count"]} for r in last_7d_submissions
            ],
        }
        return Response(data, status=status.HTTP_200_OK)
