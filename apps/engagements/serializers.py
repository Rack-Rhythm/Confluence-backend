from rest_framework import serializers
from .models import IndustryEngagement
from apps.users.models import Organization
from apps.users.serializers import OrganizationSerializer, UserProfileSerializer
from apps.issues.serializers import IssueSerializer

class IndustryEngagementSerializer(serializers.ModelSerializer):
    industry_org_details = OrganizationSerializer(source='industry_org', read_only=True)
    industry_org = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False)
    created_by_details = UserProfileSerializer(source='created_by', read_only=True)
    issue_title = serializers.CharField(source='issue.title', read_only=True)
    issue_status = serializers.CharField(source='issue.status', read_only=True)
    category = serializers.CharField(source='issue.category', read_only=True)
    district = serializers.CharField(source='issue.district', read_only=True)
    issue_photo = serializers.ImageField(source='issue.photo', read_only=True)
    issue_photo_url = serializers.CharField(source='issue.photo_url', read_only=True)
    issue_details = serializers.SerializerMethodField()
    university_name = serializers.SerializerMethodField()
    pitch_title = serializers.CharField(source='pitch.title', read_only=True, allow_null=True)
    project_title = serializers.CharField(source='project.title', read_only=True, allow_null=True)

    class Meta:
        model = IndustryEngagement
        fields = [
            'id', 'issue', 'issue_title', 'issue_status', 'category', 'district',
            'issue_photo', 'issue_photo_url', 'issue_details',
            'university_name',
            'pitch', 'pitch_title', 'project', 'project_title',
            'industry_org', 'industry_org_details',
            'created_by', 'created_by_details',
            'engagement_type', 'initiator', 'status',
            'proposal_notes', 'response_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'status', 'initiator', 'created_at', 'updated_at']

    def get_university_name(self, obj):
        if hasattr(obj.issue, 'adoption') and obj.issue.adoption and obj.issue.adoption.university:
            return obj.issue.adoption.university.name
        return None

    def get_issue_details(self, obj):
        if obj.issue:
            request = self.context.get('request')
            photo_url = None
            if obj.issue.photo:
                photo_url = request.build_absolute_uri(obj.issue.photo.url) if request else obj.issue.photo.url
            return {
                'id': obj.issue.id,
                'public_id': getattr(obj.issue, 'public_id', None),
                'title': obj.issue.title,
                'category': obj.issue.category,
                'district': obj.issue.district,
                'status': obj.issue.status,
                'photo': photo_url,
                'photo_url': obj.issue.photo_url,
            }
        return None
