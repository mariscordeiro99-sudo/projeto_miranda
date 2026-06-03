from rest_framework import serializers
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_field

from .models import (
    Announcement,
    Attachment,
    DeliveryLog,
    Document,
    Institution,
    Profile,
    PushDevice,
    VisualIdentity,
)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'created_at']


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'is_staff']


class PublicUserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'phone_number',
            'role',
            'profile_picture',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class VisualIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualIdentity
        fields = [
            'id',
            'institution',
            'logo',
            'coat_of_arms',
            'primary_color',
            'secondary_color',
            'updated_at',
        ]
        read_only_fields = ['updated_at']


class InstitutionSerializer(serializers.ModelSerializer):
    visual_identity = VisualIdentitySerializer(read_only=True)

    class Meta:
        model = Institution
        fields = [
            'id',
            'name',
            'kind',
            'official_email',
            'phone_number',
            'is_active',
            'visual_identity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            'id',
            'announcement',
            'file',
            'original_name',
            'file_type',
            'uploaded_at',
        ]
        read_only_fields = ['original_name', 'file_type', 'uploaded_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id',
            'institution',
            'author',
            'title',
            'content',
            'status',
            'pinned',
            'published_at',
            'attachments',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['author', 'published_at', 'created_at', 'updated_at']

    @extend_schema_field(PublicUserSummarySerializer)
    def get_author(self, obj):
        if not obj.author:
            return None

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and user.is_staff:
            return UserSummarySerializer(obj.author, context=self.context).data
        return PublicUserSummarySerializer(obj.author, context=self.context).data


class PushDeviceSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = PushDevice
        fields = [
            'id',
            'user',
            'token',
            'platform',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class DeliveryLogSerializer(serializers.ModelSerializer):
    recipient_user = UserSummarySerializer(read_only=True)

    class Meta:
        model = DeliveryLog
        fields = [
            'id',
            'announcement',
            'device',
            'recipient_user',
            'channel',
            'status',
            'error_message',
            'sent_at',
            'viewed_at',
            'created_at',
        ]
        read_only_fields = ['created_at']
