# jobs/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Job, Application

User = get_user_model()


# -------- משתמש מצומצם --------
class UserMiniSerializer(serializers.ModelSerializer):
    """מידע בסיסי על משתמש - לתצוגה בתוך משרה/מועמדות"""
    class Meta:
        model = User
        fields = ["id", "email"]


# -------- משרות --------
class JobListSerializer(serializers.ModelSerializer):
    """גרסה קלה לרשימת משרות - בלי תיאור מלא"""
    posted_by = UserMiniSerializer(read_only=True)
    applications_count = serializers.SerializerMethodField()  # מספר מועמדויות
    is_expired = serializers.SerializerMethodField()  # האם פג תוקף
    
    class Meta:
        model = Job
        fields = [
            "id", "title", "posted_by", "created_at", "updated_at",
            "applications_count", "is_expired"
        ]
    
    def get_applications_count(self, obj):
        """מחזיר מספר מועמדויות למשרה"""
        return obj.applications.count()
    
    def get_is_expired(self, obj):
        """בודק אם המשרה פגה (אם יש deadline במודל)"""
        # אם יש לך שדה deadline במודל Job:
        # return obj.is_expired() if hasattr(obj, 'is_expired') else False
        return False  # אם אין deadline כרגע


class JobSerializer(serializers.ModelSerializer):
    """גרסה מלאה למשרה - כולל תיאור מלא"""
    posted_by = UserMiniSerializer(read_only=True)
    applications_count = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    can_apply = serializers.SerializerMethodField()  # האם המשתמש יכול להגיש
    user_has_applied = serializers.SerializerMethodField()  # האם המשתמש הגיש

    class Meta:
        model = Job
        fields = [
            "id", "title", "description", "posted_by", 
            "created_at", "updated_at",
            "applications_count", "is_expired", "can_apply", "user_has_applied"
        ]
        read_only_fields = ["posted_by", "created_at", "updated_at"]

    def get_applications_count(self, obj):
        return obj.applications.count()
    
    def get_is_expired(self, obj):
        return False  # או obj.is_expired() אם יש
    
    def get_can_apply(self, obj):
        """בודק אם המשתמש הנוכחי יכול להגיש"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # לא יכול להגיש למשרה שלו
        if obj.posted_by == request.user:
            return False
        # כבר הגיש
        if Application.objects.filter(job=obj, applicant=request.user).exists():
            return False
        return True
    
    def get_user_has_applied(self, obj):
        """בודק אם המשתמש כבר הגיש"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Application.objects.filter(job=obj, applicant=request.user).exists()

    def create(self, validated_data):
        """יוצר משרה חדשה - posted_by אוטומטי"""
        user = self.context["request"].user
        return Job.objects.create(posted_by=user, **validated_data)


# -------- מועמדויות --------
class ApplicationSerializer(serializers.ModelSerializer):
    """להגשת מועמדות חדשה"""
    applicant = UserMiniSerializer(read_only=True)
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())

    class Meta:
        model = Application
        fields = ["id", "job", "applicant", "cover_letter", "created_at"]
        read_only_fields = ["applicant", "created_at"]

    def validate(self, attrs):
        """מוודא שלא מגישים פעמיים לאותה משרה"""
        user = self.context["request"].user
        job = attrs.get("job")
        
        # בדיקה שלא הגיש כבר
        if Application.objects.filter(job=job, applicant=user).exists():
            raise serializers.ValidationError({"job": "כבר הגשת מועמדות למשרה זו."})
        
        # בדיקה שלא מגיש למשרה שלו
        if job.posted_by == user:
            raise serializers.ValidationError({"job": "לא ניתן להגיש מועמדות למשרה שלך."})
        
        return attrs

    def create(self, validated_data):
        """יוצר מועמדות - applicant אוטומטי"""
        user = self.context["request"].user
        return Application.objects.create(applicant=user, **validated_data)


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """תצוגה מפורטת של מועמדות - כולל פרטי המשרה"""
    applicant = UserMiniSerializer(read_only=True)
    job = JobListSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ["id", "job", "applicant", "cover_letter", "created_at"]
        read_only_fields = ["applicant", "created_at"]