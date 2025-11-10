from rest_framework import viewsets, permissions, decorators, response, status
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    קריאה בלבד: רשימת ההתראות שלי + סימון כנקרא.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(to_user=self.request.user)

    @decorators.action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        obj = self.get_object()
        if not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=["is_read"])
        return response.Response({"status": "ok", "id": obj.id, "is_read": obj.is_read})

    @decorators.action(detail=False, methods=["post"])
    def read_all(self, request):
        qs = Notification.objects.filter(to_user=request.user, is_read=False)
        updated = qs.update(is_read=True)
        return response.Response({"status": "ok", "updated": updated}, status=status.HTTP_200_OK)
