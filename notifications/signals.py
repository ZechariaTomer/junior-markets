from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from jobs.models import Application
from .models import Notification
from .services import send_notification

# נשמור את הסטטוס הקודם לפני שמירה כדי לזהות שינויי סטטוס
@receiver(pre_save, sender=Application)
def store_prev_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = Application.objects.get(pk=instance.pk)
            instance._prev_status = prev.status
        except Application.DoesNotExist:
            instance._prev_status = None
    else:
        instance._prev_status = None

# התראה למגייס על יצירת מועמדות חדשה
@receiver(post_save, sender=Application)
def notify_on_application_created(sender, instance: Application, created, **kwargs):
    if created:
        recruiter = instance.job.posted_by
        send_notification(
            to_user=recruiter,
            type=Notification.Types.APPLICATION_RECEIVED,
            title="התקבלה מועמדות חדשה",
            message=f"{instance.applicant.email} הגיש/ה למשרה: {instance.job.title}",
            payload={"job_id": instance.job_id, "application_id": instance.id},
        )

# התראה למחפש העבודה על שינוי סטטוס
@receiver(post_save, sender=Application)
def notify_on_status_change(sender, instance: Application, created, **kwargs):
    if created:
        return
    prev_status = getattr(instance, "_prev_status", None)
    if prev_status is not None and prev_status != instance.status:
        seeker = instance.applicant
        send_notification(
            to_user=seeker,
            type=Notification.Types.APPLICATION_STATUS,
            title="עודכן סטטוס המועמדות",
            message=f"סטטוס למשרה '{instance.job.title}' עודכן: {prev_status} → {instance.status}",
            payload={
                "job_id": instance.job_id,
                "application_id": instance.id,
                "prev_status": prev_status,
                "new_status": instance.status,
            },
        )
