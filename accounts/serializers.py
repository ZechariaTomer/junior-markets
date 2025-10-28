from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Roles, SeekerProfile, SeekerExperience, SeekerEducation, RecruiterProfile
)

User = get_user_model()


# -------- הרשמה --------
class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": "הסיסמאות אינן תואמות"})
        validate_password(data["password1"])
        if User.objects.filter(email=data["email"].lower().strip()).exists():
            raise serializers.ValidationError({"email": "האימייל כבר רשום במערכת"})
        return data

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"].lower().strip(),
            password=validated_data["password1"],
        )


# -------- בחירת תפקיד --------
class RoleSelectSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[(Roles.SEEKER, "מחפש עבודה"), (Roles.RECRUITER, "מגייס")])

    def update(self, user, validated_data):
        user.role = validated_data["role"]
        user.save()

        # יצירת פרופיל מתאים אם לא קיים
        if user.role == Roles.SEEKER:
            SeekerProfile.objects.get_or_create(user=user)
        elif user.role == Roles.RECRUITER:
            RecruiterProfile.objects.get_or_create(user=user)

        return user


# -------- מחפש עבודה --------
class SeekerExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeekerExperience
        fields = "__all__"
        read_only_fields = ["seeker"]


class SeekerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeekerEducation
        fields = "__all__"
        read_only_fields = ["seeker"]


class SeekerProfileSerializer(serializers.ModelSerializer):
    experiences = SeekerExperienceSerializer(many=True, read_only=True)
    education = SeekerEducationSerializer(many=True, read_only=True)

    class Meta:
        model = SeekerProfile
        fields = [
            "id", "full_name", "phone", "location", "linkedin", "github", "portfolio",
            "headline", "years_experience", "skills", "languages", "about",
            "resume", "desired_level", "is_open_to_remote", "desired_salary_nis",
            "experiences", "education", "updated_at",
        ]


# -------- מגייס --------
class RecruiterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterProfile
        fields = [
            "id", "contact_name", "phone", "company_name", "company_website", "company_size",
            "company_location", "company_logo", "about_company", "notes", "updated_at",
        ]


# -------- משתמש (חדש!) --------
class UserSerializer(serializers.ModelSerializer):
    """מחזיר מידע על המשתמש + הפרופיל שלו"""
    seeker_profile = SeekerProfileSerializer(read_only=True)
    recruiter_profile = RecruiterProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "date_joined",
            "seeker_profile",    # אם SEEKER - יהיה מלא, אם RECRUITER - יהיה None
            "recruiter_profile",  # אם RECRUITER - יהיה מלא, אם SEEKER - יהיה None
        ]
        read_only_fields = ["date_joined"]