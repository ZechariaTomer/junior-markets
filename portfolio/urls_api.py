from rest_framework.routers import DefaultRouter
from .api import ProjectViewSet, ProjectImageViewSet, ProjectTagViewSet

router = DefaultRouter()
router.register(r"portfolio/projects", ProjectViewSet, basename="portfolio-project")
router.register(r"portfolio/images", ProjectImageViewSet, basename="portfolio-image")
router.register(r"portfolio/tags", ProjectTagViewSet, basename="portfolio-tag")

urlpatterns = router.urls
