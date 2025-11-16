from django.db import models
from django.conf import settings

class Project(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    title = models.CharField(max_length=120)
    summary = models.TextField(blank=True)
    repo_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    tech_stack = models.JSONField(default=list, blank=True)  # ["Django","React"]
    is_public = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to="portfolio/covers/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title} · {self.owner_id}"


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="portfolio/images/")
    caption = models.CharField(max_length=140, blank=True)

    def __str__(self):
        return f"Image#{self.id} for Project#{self.project_id}"


class ProjectTag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    projects = models.ManyToManyField(Project, related_name="tags", blank=True)

    def __str__(self):
        return self.name


