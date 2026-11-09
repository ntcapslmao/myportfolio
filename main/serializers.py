from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Project, Experience, Education, CreativeProject, PortfolioItem


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "tech_stack",
            "project_url", "project_image_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    started_at_formatted = serializers.SerializerMethodField()
    ended_at_formatted = serializers.SerializerMethodField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "organisation", "category", "category_display",
            "description", "thumbnail", "started_at", "ended_at",
            "started_at_formatted", "ended_at_formatted", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id", "category_display", "is_ongoing"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_organisation(self, value):
        value = strip_tags(value).strip()
        if not value:
            return "Personal"
        return value

    def validate_description(self, value):
        return strip_tags(value).strip()

    def validate(self, attrs):
        started_at = attrs.get("started_at") or (self.instance.started_at if self.instance else None)
        ended_at = attrs.get("ended_at", self.instance.ended_at if self.instance else None)
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError({"ended_at": "End date cannot be earlier than start date."})
        return attrs

    def get_started_at_formatted(self, obj):
        return obj.started_at.strftime("%b %Y") if obj.started_at else ""

    def get_ended_at_formatted(self, obj):
        return obj.ended_at.strftime("%b %Y") if obj.ended_at else ""

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class EducationSerializer(serializers.ModelSerializer):
    is_ongoing = serializers.BooleanField(read_only=True)
    started_at_formatted = serializers.SerializerMethodField()
    ended_at_formatted = serializers.SerializerMethodField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = [
            "id", "institution", "degree", "description",
            "started_at", "ended_at", "started_at_formatted", "ended_at_formatted",
            "is_ongoing", "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id", "is_ongoing"]

    def validate_institution(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Institution cannot be empty.")
        return value

    def validate_degree(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Degree cannot be empty.")
        return value

    def validate_description(self, value):
        if value is None:
            return ""
        return strip_tags(value).strip()

    def validate(self, attrs):
        started_at = attrs.get("started_at") or (self.instance.started_at if self.instance else None)
        ended_at = attrs.get("ended_at", self.instance.ended_at if self.instance else None)
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError({"ended_at": "End date cannot be earlier than start date."})
        return attrs

    def get_started_at_formatted(self, obj):
        return obj.started_at.strftime("%Y") if obj.started_at else ""

    def get_ended_at_formatted(self, obj):
        return obj.ended_at.strftime("%Y") if obj.ended_at else "Present"

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ["id", "title", "image_url", "video_embed_url"]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value


class CreativeProjectSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(many=True, read_only=True)
    portfolio_items = PortfolioItemSerializer(source="items", many=True, read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    started_at_formatted = serializers.SerializerMethodField()
    ended_at_formatted = serializers.SerializerMethodField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = CreativeProject
        fields = [
            "id", "title", "description", "started_at", "ended_at",
            "started_at_formatted", "ended_at_formatted", "date_added",
            "is_ongoing", "items", "portfolio_items",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id", "date_added", "is_ongoing"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value).strip()

    def validate(self, attrs):
        started_at = attrs.get("started_at") or (self.instance.started_at if self.instance else None)
        ended_at = attrs.get("ended_at", self.instance.ended_at if self.instance else None)
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError({"ended_at": "End date cannot be earlier than start date."})
        return attrs

    def get_started_at_formatted(self, obj):
        return obj.started_at.strftime("%b %Y") if obj.started_at else ""

    def get_ended_at_formatted(self, obj):
        return obj.ended_at.strftime("%b %Y") if obj.ended_at else "Present"

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())
