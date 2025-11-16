from rest_framework import viewsets, permissions, decorators, response, status
from .models import Project, ProjectImage, ProjectTag
from .serializers import ProjectSerializer, ProjectImageSerializer, ProjectTagSerializer
from .permissions import IsOwnerOrReadOnly

class ProjectViewSet(viewsets.ModelViewSet):
    """
    פרויקטים בפורטפוליו.
    - list/retrieve: ציבורי (מציג רק פרויקטים is_public=True)
    - create/update/destroy: למשתמש מחובר; עדכון/מחיקה רק לבעל הפרויקט
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Project.objects.select_related("owner").prefetch_related("images", "tags")
        if self.action in ["list", "retrieve"]:
            # תצוגה ציבורית – רק פרויקטים גלויים
            return qs.filter(is_public=True)
        # פעולות מנהליות – נשתמש ב-object permissions בביצוע
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @decorators.action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def my_projects(self, request):
        """רשימת כל הפרויקטים של המשתמש המחובר (כולל פרטיים)"""
        qs = Project.objects.filter(owner=request.user).prefetch_related("images", "tags")
        return response.Response(ProjectSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class ProjectImageViewSet(viewsets.ModelViewSet):
    """
    תמונות של פרויקט – בעל הפרויקט בלבד יכול להוסיף/למחוק.
    """
    serializer_class = ProjectImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # המשתמש רואה תמונות של הפרויקטים שלו; לציבורי אפשר להרחיב לפי צורך
        if not self.request.user.is_authenticated:
            return ProjectImage.objects.none()
        return ProjectImage.objects.filter(project__owner=self.request.user)

    def perform_create(self, serializer):
        # דורש פרמטר project_id ב-body או ב-query
        project_id = self.request.data.get("project") or self.request.query_params.get("project")
        if not project_id:
            return  # DRF יחזיר 400 בגלל שדה חסר
        # אימות בעלות פשוט
        from .models import Project
        project = Project.objects.get(pk=project_id)
        if project.owner_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("אפשר להעלות תמונות רק לפרויקטים שלך.")
        serializer.save(project=project)


class ProjectTagViewSet(viewsets.ModelViewSet):
    """
    תגיות לפרויקטים – מנהלות פשוטות; כרגע פתוח למנהלים בלבד (ניתן לשנות).
    """
    queryset = ProjectTag.objects.all().order_by("name")
    serializer_class = ProjectTagSerializer
    permission_classes = [permissions.IsAdminUser]
