from rest_framework.routers import DefaultRouter
from .api import NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls
