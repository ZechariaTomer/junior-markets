from rest_framework import generics, permissions, viewsets
from rest_framework.parsers import MultiPartParser, FormParser  # ← לקבצים
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import (
    Roles, SeekerProfile, SeekerExperience, SeekerEducation, RecruiterProfile
)
from .serializers import (
    SignupSerializer, RoleSelectSerializer,
    SeekerProfileSerializer, SeekerExperienceSerializer, SeekerEducationSerializer,
    RecruiterProfileSerializer
)

User = get_user_model()

# --- Auth ---
class SignupAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupSerializer


# --- Role selection ---
class RoleSelectAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]        # ← רק מחובר
    serializer_class = RoleSelectSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.update(request.user, serializer.validated_data)
        return Response({"role": user.role})


# --- Seeker ---
class SeekerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = SeekerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]            # ← תמיכה ב-upload (resume)

    def get_queryset(self):
        return SeekerProfile.objects.filter(user=self.request.user)

    def get_object(self):
        obj, _ = SeekerProfile.objects.get_or_create(user=self.request.user)
        return obj

    def list(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        # אין יצירה כפולה – משתמש אחד = פרופיל אחד
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SeekerExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = SeekerExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile, _ = SeekerProfile.objects.get_or_create(user=self.request.user)
        return SeekerExperience.objects.filter(seeker=profile)

    def perform_create(self, serializer):
        profile, _ = SeekerProfile.objects.get_or_create(user=self.request.user
        )
        serializer.save(seeker=profile)


class SeekerEducationViewSet(viewsets.ModelViewSet):
    serializer_class = SeekerEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile, _ = SeekerProfile.objects.get_or_create(user=self.request.user)
        return SeekerEducation.objects.filter(seeker=profile)

    def perform_create(self, serializer):
        profile, _ = SeekerProfile.objects.get_or_create(user=self.request.user)
        serializer.save(seeker=profile)


# --- Recruiter ---
class RecruiterProfileViewSet(viewsets.ModelViewSet):
    serializer_class = RecruiterProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]            # ← תמיכה ב-upload (company_logo)

    def get_queryset(self):
        return RecruiterProfile.objects.filter(user=self.request.user)

    def get_object(self):
        obj, _ = RecruiterProfile.objects.get_or_create(user=self.request.user)
        return obj

    def list(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    def create(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
# --- Current User ---
class MeAPIView(generics.RetrieveAPIView):
    """
    מחזיר את המשתמש המחובר + הפרופיל שלו
    GET /api/auth/me/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from .serializers import UserSerializer
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
