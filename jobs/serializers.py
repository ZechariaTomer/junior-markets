# jobs/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Job, Application

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]  # username נשמר לתאימות; ההתחברות אצלך עם email


class JobSerializer(serializers.ModelSerializer):
    posted_by = UserMiniSerializer(read_only=True)

    class Meta:
        model = Job
        fields = ["id", "title", "description", "posted_by", "created_at", "updated_at"]
        read_only_fields = ["posted_by", "created_at", "updated_at"]

    def create(self, validated_data):
        # posted_by נקבע אוטומטית לפי המשתמש המחובר
        user = self.context["request"].user
        return Job.objects.create(posted_by=user, **validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = UserMiniSerializer(read_only=True)
    # הלקוח שולח מזהה משרה בלבד
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())

    class Meta:
        model = Application
        fields = ["id", "job", "applicant", "cover_letter", "created_at"]
        read_only_fields = ["applicant", "created_at"]

    def validate(self, attrs):
        """
        מוודא שלא מגישים פעמיים לאותה משרה (בנוסף ל-unique_together במסד).
        """
        user = self.context["request"].user
        job = attrs.get("job")
        if Application.objects.filter(job=job, applicant=user).exists():
            raise serializers.ValidationError("כבר הגשת מועמדות למשרה זו.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Application.objects.create(applicant=user, **validated_data)
