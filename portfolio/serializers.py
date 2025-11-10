from rest_framework import serializers
from .models import Project, ProjectImage, ProjectTag

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "project", "image", "caption"]
        read_only_fields = ["project"]  # נגדיר project באקשן create בצד ה-ViewSet כשצריך

class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ["id", "name"]

class ProjectSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)
    tags = ProjectTagSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "owner", "title", "summary",
            "repo_url", "demo_url", "tech_stack",
            "is_public", "cover_image",
            "images", "tags",
            "created_at",
        ]
        read_only_fields = ["owner", "created_at"]
