from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import parsers, permissions, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .audit import record_audit_log
from .delivery import create_pending_delivery_logs, dispatch_published_announcement
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
from .media_processing import prepare_attachment
from .media_validation import attachment_type
from .privacy import process_privacy_request
from .reports import build_dashboard_report
from .serializers import (
    AnnouncementSerializer,
    AttachmentSerializer,
    AuditLogSerializer,
    DeliveryLogSerializer,
    DocumentSerializer,
    InstitutionSerializer,
    ManagerSerializer,
    PrivacyRequestSerializer,
    ProfileSerializer,
    PushDeviceSerializer,
    SegmentSerializer,
    VisualIdentitySerializer,
)
from .services import PushNotificationService


class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class NoDestroyModelViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']


class HelloView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses=inline_serializer(
            name='HelloResponse',
            fields={
                'message': serializers.CharField(),
                'status': serializers.CharField(),
                'version': serializers.CharField(),
            },
        )
    )
    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Olá do backend Django! A comunicação está funcionando.',
            'status': 'healthy',
            'version': '1.0.0',
        })


class DashboardReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        responses=inline_serializer(
            name='DashboardReportResponse',
            fields={
                'users': serializers.DictField(),
                'announcements': serializers.DictField(),
                'delivery': serializers.DictField(),
                'devices': serializers.DictField(),
                'recent_announcements': serializers.ListField(
                    child=serializers.DictField()
                ),
            },
        )
    )
    def get(self, request, *args, **kwargs):
        return Response(build_dashboard_report())


class DocumentViewSet(NoDestroyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsManagerOrReadOnly]
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at']
    ordering = ['-created_at']


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role', 'user']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'phone_number']
    ordering_fields = ['created_at', 'updated_at', 'user__username']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Profile.objects.select_related('user').all()
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return queryset.none()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['action', 'target_type', 'actor']
    search_fields = ['action', 'actor_username', 'target_repr', 'target_id']
    ordering_fields = ['created_at', 'action', 'target_type', 'actor_username']
    ordering = ['-created_at']

    def get_queryset(self):
        return AuditLog.objects.select_related('actor').all()


class PrivacyRequestViewSet(viewsets.ModelViewSet):
    serializer_class = PrivacyRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']
    filterset_fields = ['request_type', 'status', 'user', 'resolved_by']
    search_fields = ['requester_name', 'requester_email', 'notes']
    ordering_fields = ['created_at', 'resolved_at', 'status', 'request_type']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = PrivacyRequest.objects.select_related('user', 'resolved_by').all()
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return queryset.none()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in ['partial_update', 'complete', 'reject']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        privacy_request = serializer.save(
            user=user,
            requester_name=serializer.validated_data.get('requester_name') or user.get_full_name() or user.username,
            requester_email=serializer.validated_data.get('requester_email') or user.email,
        )
        record_audit_log(
            user,
            'privacy_request_created',
            privacy_request,
            {'request_type': privacy_request.request_type},
        )

    def perform_update(self, serializer):
        privacy_request = serializer.save(
            resolved_by=self.request.user,
            resolved_at=timezone.now(),
        )
        record_audit_log(
            self.request.user,
            'privacy_request_updated',
            privacy_request,
            {'status': privacy_request.status},
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None, **kwargs):
        privacy_request = self.get_object()
        privacy_request, result = process_privacy_request(
            privacy_request,
            request.user,
            notes=request.data.get('notes'),
        )
        record_audit_log(
            request.user,
            'privacy_request_completed',
            privacy_request,
            {
                'request_type': privacy_request.request_type,
                'action': result['action'],
                'summary': result.get('summary', {}),
            },
        )
        data = self.get_serializer(privacy_request).data
        data['lgpd_action'] = result['action']
        data['lgpd_summary'] = result.get('summary', {})
        if 'export' in result:
            data['export'] = result['export']
        return Response(data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None, **kwargs):
        privacy_request = self.get_object()
        privacy_request.status = PrivacyRequest.STATUS_REJECTED
        privacy_request.notes = request.data.get('notes', privacy_request.notes)
        privacy_request.resolved_by = request.user
        privacy_request.resolved_at = timezone.now()
        privacy_request.save(update_fields=['status', 'notes', 'resolved_by', 'resolved_at'])
        record_audit_log(
            request.user,
            'privacy_request_rejected',
            privacy_request,
            {'request_type': privacy_request.request_type},
        )
        return Response(self.get_serializer(privacy_request).data)


class DeactivateOwnAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        responses=inline_serializer(
            name='DeactivateOwnAccountResponse',
            fields={'detail': serializers.CharField()},
        )
    )
    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            return Response(
                {'detail': 'Use a gestão de administradores para desativar contas administrativas.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        Token.objects.filter(user=user).delete()
        record_audit_log(user, 'account_deactivated_by_owner', user)
        return Response(
            {'detail': 'Conta desativada com sucesso.'},
            status=status.HTTP_200_OK,
        )


class ManagerViewSet(viewsets.ModelViewSet):
    serializer_class = ManagerSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['is_active', 'is_staff', 'profile__role']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'profile__phone_number']
    ordering_fields = ['username', 'email', 'first_name', 'is_active', 'date_joined']
    ordering = ['-is_active', 'username']

    def get_queryset(self):
        return (
            User.objects
            .select_related('profile')
            .filter(Q(is_staff=True) | Q(profile__role=Profile.ROLE_MANAGER))
            .distinct()
            .order_by('-is_active', 'username')
        )

    def perform_create(self, serializer):
        manager = serializer.save()
        record_audit_log(self.request.user, 'manager_created', manager)

    def perform_update(self, serializer):
        manager = serializer.save()
        record_audit_log(self.request.user, 'manager_updated', manager)

    def destroy(self, request, *args, **kwargs):
        manager = self.get_object()
        if self.is_self_action(manager):
            return Response(
                {'detail': 'Você não pode desativar seu próprio acesso.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager.is_active = False
        manager.save(update_fields=['is_active'])
        record_audit_log(request.user, 'manager_deactivated', manager)
        return Response(self.get_serializer(manager).data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None, **kwargs):
        manager = self.get_object()
        if self.is_self_action(manager):
            return Response(
                {'detail': 'Você não pode desativar seu próprio acesso.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager.is_active = False
        manager.save(update_fields=['is_active'])
        record_audit_log(request.user, 'manager_deactivated', manager)
        return Response(self.get_serializer(manager).data)

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None, **kwargs):
        manager = self.get_object()
        manager.is_active = True
        manager.is_staff = True
        manager.save(update_fields=['is_active', 'is_staff'])
        profile, _ = Profile.objects.get_or_create(user=manager)
        profile.role = Profile.ROLE_MANAGER
        profile.save(update_fields=['role'])
        record_audit_log(request.user, 'manager_reactivated', manager)
        return Response(self.get_serializer(manager).data)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None, **kwargs):
        manager = self.get_object()
        if self.is_self_action(manager):
            return Response(
                {'detail': 'Você não pode revogar seu próprio acesso.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager.is_staff = False
        manager.save(update_fields=['is_staff'])
        Token.objects.filter(user=manager).delete()

        profile, _ = Profile.objects.get_or_create(user=manager)
        profile.role = Profile.ROLE_CITIZEN
        profile.save(update_fields=['role'])
        record_audit_log(request.user, 'manager_revoked', manager)
        return Response(self.get_serializer(manager).data)

    def is_self_action(self, manager):
        return self.request.user.is_authenticated and manager.id == self.request.user.id


class InstitutionViewSet(NoDestroyModelViewSet):
    queryset = Institution.objects.prefetch_related('visual_identity').all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsManagerOrReadOnly]
    filterset_fields = ['kind', 'is_active']
    search_fields = ['name', 'official_email', 'phone_number']
    ordering_fields = ['name', 'kind', 'is_active', 'created_at', 'updated_at']
    ordering = ['name']


class SegmentViewSet(NoDestroyModelViewSet):
    queryset = Segment.objects.prefetch_related('users', 'push_devices').all()
    serializer_class = SegmentSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['is_active']
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'slug', 'created_at', 'updated_at']
    ordering = ['name']

    def perform_create(self, serializer):
        segment = serializer.save()
        record_audit_log(self.request.user, 'segment_created', segment)

    def perform_update(self, serializer):
        segment = serializer.save()
        record_audit_log(self.request.user, 'segment_updated', segment)


class VisualIdentityViewSet(NoDestroyModelViewSet):
    queryset = VisualIdentity.objects.select_related('institution').all()
    serializer_class = VisualIdentitySerializer
    permission_classes = [IsManagerOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ['institution']
    search_fields = ['institution__name']
    ordering_fields = ['updated_at', 'institution__name']
    ordering = ['-updated_at']

    def perform_create(self, serializer):
        visual_identity = serializer.save()
        record_audit_log(self.request.user, 'visual_identity_created', visual_identity)

    def perform_update(self, serializer):
        visual_identity = serializer.save()
        record_audit_log(self.request.user, 'visual_identity_updated', visual_identity)


class AnnouncementViewSet(NoDestroyModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsManagerOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ['status', 'institution', 'author', 'pinned', 'segments']
    search_fields = ['title', 'content', 'institution__name', 'author__username']
    ordering_fields = [
        'title',
        'status',
        'pinned',
        'published_at',
        'created_at',
        'updated_at',
    ]
    ordering = ['-pinned', '-published_at', '-created_at']

    def get_queryset(self):
        queryset = (
            Announcement.objects.select_related('author', 'institution')
            .prefetch_related('attachments', 'segments')
            .all()
        )
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(status=Announcement.STATUS_PUBLISHED)

    def perform_create(self, serializer):
        files = self.prepare_attachment_files()
        announcement = serializer.save(author=self.request.user)
        self.create_attachments(announcement, files)
        record_audit_log(self.request.user, 'announcement_created', announcement)
        if announcement.status == Announcement.STATUS_PUBLISHED:
            self.push_dispatch_result = dispatch_published_announcement(announcement)

    def perform_update(self, serializer):
        files = self.prepare_attachment_files()
        was_published = serializer.instance.status == Announcement.STATUS_PUBLISHED
        announcement = serializer.save()
        self.create_attachments(announcement, files)
        record_audit_log(self.request.user, 'announcement_updated', announcement)
        if not was_published and announcement.status == Announcement.STATUS_PUBLISHED:
            self.push_dispatch_result = dispatch_published_announcement(announcement)

    def get_attachment_files(self):
        files = []
        files.extend(self.request.FILES.getlist('attachments'))
        files.extend(self.request.FILES.getlist('files'))
        return files

    def prepare_attachment_files(self):
        return [
            prepare_attachment(uploaded_file)
            for uploaded_file in self.get_attachment_files()
        ]

    def create_attachments(self, announcement, files):
        for uploaded_file in files:
            Attachment.objects.create(
                announcement=announcement,
                file=uploaded_file,
                original_name=uploaded_file.name,
                file_type=attachment_type(uploaded_file),
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def publish(self, request, pk=None, **kwargs):
        announcement = self.get_object()
        was_published = announcement.status == Announcement.STATUS_PUBLISHED
        announcement.status = Announcement.STATUS_PUBLISHED
        announcement.published_at = announcement.published_at or timezone.now()
        announcement.save(update_fields=['status', 'published_at', 'updated_at'])
        if not was_published:
            record_audit_log(request.user, 'announcement_published', announcement)
            self.push_dispatch_result = dispatch_published_announcement(announcement)

        data = self.get_serializer(announcement).data
        if hasattr(self, 'push_dispatch_result'):
            data['push_dispatch'] = self.push_dispatch_result
        return Response(data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
        url_path='dispatch',
        url_name='dispatch',
    )
    def dispatch_push(self, request, pk=None, **kwargs):
        announcement = self.get_object()
        create_pending_delivery_logs(announcement)
        result = PushNotificationService().dispatch_pending_for_announcement(announcement)
        record_audit_log(
            request.user,
            'announcement_push_dispatched',
            announcement,
            {
                'configured': result['configured'],
                'sent': result['sent'],
                'failed': result['failed'],
                'pending': result['pending'],
            },
        )
        return Response(
            {
                'detail': 'Disparo de notificações processado.',
                'provider_configured': result['configured'],
                'sent': result['sent'],
                'failed': result['failed'],
                'pending': result['pending'],
                'total_logs': announcement.delivery_logs.count(),
            }
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request, pk=None, **kwargs):
        announcement = self.get_object()
        logs = announcement.delivery_logs.all()
        failed_logs = logs.filter(status=DeliveryLog.STATUS_FAILED)
        total = logs.count()
        viewed = logs.filter(status=DeliveryLog.STATUS_VIEWED).count()
        return Response(
            {
                'announcement': announcement.id,
                'pending': logs.filter(status=DeliveryLog.STATUS_PENDING).count(),
                'sent': logs.filter(status=DeliveryLog.STATUS_SENT).count(),
                'failed': failed_logs.count(),
                'viewed': viewed,
                'total': total,
                'view_rate': round((viewed / total) * 100, 2) if total else 0.0,
                'failed_errors': [
                    {
                        'log_id': log.id,
                        'device_id': log.device_id,
                        'device_is_active': log.device.is_active if log.device else None,
                        'error_message': log.error_message,
                    }
                    for log in failed_logs.select_related('device')
                ],
            }
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.AllowAny],
        url_path='mark-viewed',
        url_name='mark-viewed',
    )
    def mark_viewed(self, request, pk=None, **kwargs):
        announcement = self.get_object()
        delivery_log_id = request.data.get('delivery_log_id') or request.data.get('log_id')
        device_token = request.data.get('device_token') or request.data.get('token')

        logs = DeliveryLog.objects.filter(announcement=announcement).select_related('device')
        if delivery_log_id:
            logs = logs.filter(id=delivery_log_id)
        elif request.user.is_authenticated:
            logs = logs.filter(recipient_user=request.user)
        elif device_token:
            logs = logs.filter(device__token=device_token)
        else:
            return Response(
                {'detail': 'Autenticação, delivery_log_id ou device_token é obrigatório.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        log = logs.order_by('-created_at').first()
        if not log:
            return Response(
                {'detail': 'Log de entrega não encontrado para este comunicado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self.can_mark_log_viewed(request, log, device_token):
            return Response({'detail': 'Ação não permitida.'}, status=status.HTTP_403_FORBIDDEN)

        self.mark_log_viewed(log)
        return Response(
            {
                'detail': 'Comunicado marcado como visualizado.',
                'delivery_log': DeliveryLogSerializer(log).data,
            }
        )

    def can_mark_log_viewed(self, request, log, device_token):
        if request.user.is_authenticated:
            if request.user.is_staff or log.recipient_user_id == request.user.id:
                return True

        return bool(device_token and log.device and log.device.token == device_token)

    def mark_log_viewed(self, log):
        if log.status == DeliveryLog.STATUS_VIEWED and log.viewed_at:
            return

        log.status = DeliveryLog.STATUS_VIEWED
        log.viewed_at = timezone.now()
        log.save(update_fields=['status', 'viewed_at'])


class AttachmentViewSet(NoDestroyModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [IsManagerOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ['announcement', 'file_type']
    search_fields = ['original_name', 'announcement__title']
    ordering_fields = ['uploaded_at', 'original_name', 'file_type']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        queryset = Attachment.objects.select_related('announcement').all()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(announcement__status=Announcement.STATUS_PUBLISHED)

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get('file')
        if uploaded_file:
            prepared_file = prepare_attachment(uploaded_file)
            serializer.save(
                file=prepared_file,
                original_name=prepared_file.name,
                file_type=attachment_type(prepared_file),
            )
        else:
            serializer.save()


class PushDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = PushDeviceSerializer
    parser_classes = [parsers.JSONParser, parsers.FormParser]
    filterset_fields = ['platform', 'is_active', 'user']
    search_fields = ['token', 'user__username', 'user__email']
    ordering_fields = ['platform', 'is_active', 'created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        queryset = PushDevice.objects.select_related('user').all()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        return PushDevice.objects.none()

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return Response({'detail': 'Token é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        defaults = {
            'platform': request.data.get('platform', PushDevice.PLATFORM_WEB),
            'is_active': True,
        }
        if request.user.is_authenticated:
            defaults['user'] = request.user

        device, _ = PushDevice.objects.update_or_create(token=token, defaults=defaults)
        serializer = self.get_serializer(device)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeliveryLogViewSet(NoDestroyModelViewSet):
    serializer_class = DeliveryLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['status', 'channel', 'announcement', 'device', 'recipient_user']
    search_fields = ['error_message', 'announcement__title', 'device__token', 'recipient_user__username']
    ordering_fields = ['created_at', 'sent_at', 'viewed_at', 'status', 'channel']
    ordering = ['-created_at']

    def get_queryset(self):
        return DeliveryLog.objects.select_related(
            'announcement',
            'device',
            'recipient_user',
        ).all()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_viewed(self, request, pk=None, **kwargs):
        log = self.get_object()
        if not request.user.is_staff and log.recipient_user_id != request.user.id:
            return Response({'detail': 'Ação não permitida.'}, status=status.HTTP_403_FORBIDDEN)
        log.status = DeliveryLog.STATUS_VIEWED
        log.viewed_at = timezone.now()
        log.save(update_fields=['status', 'viewed_at'])
        return Response(self.get_serializer(log).data)
