from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # API
    path("api/", include("accounts.urls_api")),  # חייב להיות קיים בפרויקט
    path("api/", include("jobs.urls_api")),      # הקובץ שהכנת (jobs/urls_api.py)
    path("api/", include("portfolio.urls_api")),
    path("api/", include("notifications.urls_api")),
    path("api/", include("statsapi.urls_api")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)