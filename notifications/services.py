from .models import Notification

def send_notification(*, to_user, type, title, message="", payload=None):
    return Notification.objects.create(
        to_user=to_user,
        type=type,
        title=title,
        message=message or "",
        payload=payload or {},
    )
