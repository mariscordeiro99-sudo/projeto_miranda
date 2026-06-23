from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import (
    Announcement,
    Attachment,
    AuditLog,
    DeliveryLog,
    Document,
    Institution,
    PrivacyRequest,
    Profile,
    PushDevice,
    Segment,
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
            'manager_access_requested',
            'can_control_access',
            'can_manage_announcements',
            'can_manage_visual_identity',
            'can_view_manager_dashboard',
            'profile_picture',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ManagerSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        style={'input_type': 'password'},
    )
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'phone_number',
            'is_active',
            'is_staff',
            'role',
            'date_joined',
            'password',
        ]
        read_only_fields = ['id', 'is_staff', 'role', 'date_joined']

    def get_role(self, obj) -> str | None:
        profile = getattr(obj, 'profile', None)
        return profile.role if profile else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = getattr(instance, 'profile', None)
        data['phone_number'] = profile.phone_number if profile else ''
        return data

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'Senha obrigatória.'})

        username = attrs.get('username')
        if self.instance is None and not username:
            raise serializers.ValidationError({'username': 'Usuário obrigatório.'})

        email = attrs.get('email', '')
        if self.instance is None and not email:
            raise serializers.ValidationError({'email': 'E-mail obrigatório.'})

        user_id = self.instance.id if self.instance else None
        if username and User.objects.exclude(id=user_id).filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Este usuário já existe.'})

        if email and User.objects.exclude(id=user_id).filter(email__iexact=email).exists():
            raise serializers.ValidationError({'email': 'Este e-mail já existe.'})

        password = attrs.get('password')
        if password:
            candidate = self.instance or User(
                username=username or '',
                email=email,
                first_name=attrs.get('first_name', ''),
            )
            try:
                validate_password(password, user=candidate)
            except ValidationError as error:
                raise serializers.ValidationError({'password': list(error.messages)})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number', '')
        password = validated_data.pop('password')
        is_active = validated_data.pop('is_active', True)
        user = User(
            **validated_data,
            is_staff=True,
            is_active=is_active,
        )
        user.set_password(password)
        user.save()
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'phone_number': phone_number,
                'role': Profile.ROLE_MANAGER,
                'manager_access_requested': False,
                'can_control_access': True,
                'can_manage_announcements': True,
                'can_manage_visual_identity': True,
                'can_view_manager_dashboard': True,
            },
        )
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        password = validated_data.pop('password', None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.is_staff = True
        if password:
            instance.set_password(password)
        instance.save()

        profile, _ = Profile.objects.get_or_create(user=instance)
        if phone_number is not None:
            profile.phone_number = phone_number
        profile.role = Profile.ROLE_MANAGER
        profile.manager_access_requested = False
        profile.can_control_access = True
        profile.can_manage_announcements = True
        profile.can_manage_visual_identity = True
        profile.can_view_manager_dashboard = True
        profile.save()
        return instance


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


class SegmentSerializer(serializers.ModelSerializer):
    users_count = serializers.SerializerMethodField()
    push_devices_count = serializers.SerializerMethodField()

    class Meta:
        model = Segment
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'users',
            'push_devices',
            'users_count',
            'push_devices_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'users_count', 'push_devices_count']

    def get_users_count(self, obj) -> int:
        return obj.users.count()

    def get_push_devices_count(self, obj) -> int:
        return obj.push_devices.count()


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
    segments = serializers.PrimaryKeyRelatedField(
        queryset=Segment.objects.filter(is_active=True),
        many=True,
        required=False,
    )

    class Meta:
        model = Announcement
        fields = [
            'id',
            'institution',
            'author',
            'title',
            'content',
            'status',
            'segments',
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


class AuditLogSerializer(serializers.ModelSerializer):
    actor = UserSummarySerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'actor',
            'actor_username',
            'action',
            'target_type',
            'target_id',
            'target_repr',
            'metadata',
            'created_at',
        ]
        read_only_fields = fields


class PrivacyRequestSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    resolved_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = PrivacyRequest
        fields = [
            'id',
            'user',
            'requester_name',
            'requester_email',
            'request_type',
            'status',
            'notes',
            'created_at',
            'resolved_at',
            'resolved_by',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'created_at',
            'resolved_at',
            'resolved_by',
        ]

    def validate_requester_email(self, value):
        if not value and self.context.get('request') and self.context['request'].user.email:
            return self.context['request'].user.email
        return value
