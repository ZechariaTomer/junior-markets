# accounts/urls_api.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api import (
    SignupAPIView, RoleSelectAPIView,
    SeekerProfileViewSet, SeekerExperienceViewSet, SeekerEducationViewSet,
    RecruiterProfileViewSet
)

router = DefaultRouter()
router.register(r"seeker/profile", SeekerProfileViewSet, basename="seeker-profile")
router.register(r"seeker/experiences", SeekerExperienceViewSet, basename="seeker-exp")
router.register(r"seeker/education", SeekerEducationViewSet, basename="seeker-edu")
router.register(r"recruiter/profile", RecruiterProfileViewSet, basename="recruiter-profile")

urlpatterns = [
    path("auth/signup/", SignupAPIView.as_view(), name="api-signup"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("accounts/select-role/", RoleSelectAPIView.as_view(), name="api-select-role"),
    path("", include(router.urls)),
]

