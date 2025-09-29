
# accounts/views.py
from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


def healthcheck(request):
    """
    סטטוס כללי של השרת + DB
    """
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
    except Exception:
        db_ok = False

    return JsonResponse({
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def healthcheck_auth(request):
    """
    סטטוס בריאות עם אימות JWT.
    מחזיר גם את האימייל של המשתמש ואת ה-role שלו.
    """
    return JsonResponse({
        "status": "ok",
        "user": request.user.email,
        "role": request.user.role,
    })

