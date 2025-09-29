# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# אם שתי הפונקציות קיימות ב-accounts.views השאירו את שתי היבואות.
# אם אין לכם healthcheck_auth – הסירו את היבוא ואת הנתיב שלו למטה.
from accounts.views import healthcheck, healthcheck_auth  # הסר/י healthcheck_auth אם לא קיים

urlpatterns = [
    path("admin/", admin.site.urls),

    # APIs
    path("api/", include("accounts.urls_api")),
    path("api/jobs/", include("jobs.urls_api")),

    # אם יש לכם app בשם market עם urls.py – השאירו את זה. אחרת מחקו את השורה.
    path("api/market/", include("market.urls")),

    # Health endpoints
    path("health/", healthcheck),
    path("api/health-auth/", healthcheck_auth),  # הסר/י אם אין פונקציה כזו
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
