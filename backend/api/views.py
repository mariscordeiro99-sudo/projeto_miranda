from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone
from rest_framework import parsers, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

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
from .serializers import (
    AnnouncementSerializer,
    AttachmentSerializer,
    DeliveryLogSerializer,
    DocumentSerializer,
    InstitutionSerializer,
    ProfileSerializer,
    PushDeviceSerializer,
    VisualIdentitySerializer,
)
from .services import PushNotificationService


MAX_ATTACHMENT_SIZE = 60 * 1024 * 1024
ALLOWED_ATTACHMENT_CONTENT_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png',
    'image/webp',
    'video/mp4',
    'video/quicktime',
    'video/webm',
}


def attachment_type(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type.startswith('image/'):
        return Attachment.TYPE_IMAGE
    if content_type.startswith('video/'):
        return Attachment.TYPE_VIDEO
    if content_type in {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }:
        return Attachment.TYPE_DOCUMENT
    return Attachment.TYPE_OTHER


def validate_attachment(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type not in ALLOWED_ATTACHMENT_CONTENT_TYPES:
        raise DRFValidationError(f'Unsupported attachment type: {content_type or "unknown"}.')
    if uploaded_file.size > MAX_ATTACHMENT_SIZE:
        raise DRFValidationError('Attachment exceeds the 60MB limit.')


class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class HelloView(APIView):
    def get(self, request):
        return Response({
            'message': 'Olá do backend Django! A comunicação está funcionando.',
            'status': 'healthy',
            'version': '1.0.0',
        })


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '')
        phone = request.data.get('telefone', '') or request.data.get('phone_number', '')
        is_gestor = str(request.data.get('isGestor', '') or request.data.get('is_gestor', '')).lower() in ('true', '1', 'yes')

        if not username or not email or not password:
            return Response(
                {'detail': 'username, email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'detail': 'username already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'email already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=phone,
            is_staff=is_gestor,
        )
        user.set_password(password)
        user.save()
        Profile.objects.create(
            user=user,
            phone_number=phone,
            role=Profile.ROLE_MANAGER if is_gestor else Profile.ROLE_CITIZEN,
            profile_picture=request.FILES.get('profile_picture'),
        )

        return Response(
            {
                'message': 'User registered successfully.',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args, **kwargs):
        login_value = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not login_value or not password:
            return Response(
                {'detail': 'username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = None
        password_is_valid = False
        if '@' in login_value:
            user = User.objects.filter(email__iexact=login_value).first()
            password_is_valid = bool(user and user.is_active and user.check_password(password))
        elif login_value.isdigit():
            user = User.objects.filter(last_name=login_value).first()
            password_is_valid = bool(user and user.is_active and user.check_password(password))
        else:
            user = authenticate(request, username=login_value, password=password)
            password_is_valid = user is not None

        if not password_is_valid:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'access_token': token.key,
                'token': token.key,
                'token_type': 'bearer',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'is_staff': user.is_staff,
                },
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        identifier = request.data.get('email', '') or request.data.get('username', '')
        identifier = identifier.strip()

        if not identifier:
            return Response(
                {'detail': 'email is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=identifier).first()
        if user and user.is_active and user.email:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
            reset_url = f'{frontend_url}/reset-password?uid={uid}&token={token}'

            send_mail(
                subject='Redefinicao de senha - Projeto Miranda',
                message=(
                    'Recebemos uma solicitacao para redefinir sua senha.\n\n'
                    f'Acesse este link para criar uma nova senha:\n{reset_url}\n\n'
                    'Se voce nao solicitou isso, ignore este e-mail.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response(
            {'detail': 'If the account exists, a password reset email was sent.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '') or request.data.get('password', '')

        if not uid or not token or not new_password:
            return Response(
                {'detail': 'uid, token and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, UnicodeDecodeError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Invalid or expired password reset token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=user)
        except ValidationError as error:
            return Response(
                {'detail': list(error.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response(
            {'detail': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK,
        )


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsManagerOrReadOnly]


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Profile.objects.select_related('user').all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.prefetch_related('visual_identity').all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsManagerOrReadOnly]


class VisualIdentityViewSet(viewsets.ModelViewSet):
    queryset = VisualIdentity.objects.select_related('institution').all()
    serializer_class = VisualIdentitySerializer
    permission_classes = [IsManagerOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsManagerOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        queryset = (
            Announcement.objects.select_related('author', 'institution')
            .prefetch_related('attachments')
            .all()
        )
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        return queryset.filter(status=Announcement.STATUS_PUBLISHED)

    def perform_create(self, serializer):
        announcement = serializer.save(author=self.request.user)
        self.create_attachments(announcement)
        if announcement.status == Announcement.STATUS_PUBLISHED:
            self.create_pending_delivery_logs(announcement)

    def perform_update(self, serializer):
        was_published = serializer.instance.status == Announcement.STATUS_PUBLISHED
        announcement = serializer.save()
        self.create_attachments(announcement)
        if not was_published and announcement.status == Announcement.STATUS_PUBLISHED:
            self.create_pending_delivery_logs(announcement)

    def create_attachments(self, announcement):
        files = []
        files.extend(self.request.FILES.getlist('attachments'))
        files.extend(self.request.FILES.getlist('files'))
        for uploaded_file in files:
            validate_attachment(uploaded_file)
            Attachment.objects.create(
                announcement=announcement,
                file=uploaded_file,
                original_name=uploaded_file.name,
                file_type=attachment_type(uploaded_file),
            )

    def create_pending_delivery_logs(self, announcement):
        devices = PushDevice.objects.filter(is_active=True).select_related('user')
        logs = [
            DeliveryLog(
                announcement=announcement,
                device=device,
                recipient_user=device.user,
                status=DeliveryLog.STATUS_PENDING,
            )
            for device in devices
        ]
        DeliveryLog.objects.bulk_create(logs, ignore_conflicts=True)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def publish(self, request, pk=None):
        announcement = self.get_object()
        was_published = announcement.status == Announcement.STATUS_PUBLISHED
        announcement.status = Announcement.STATUS_PUBLISHED
        announcement.published_at = announcement.published_at or timezone.now()
        announcement.save(update_fields=['status', 'published_at', 'updated_at'])
        if not was_published:
            self.create_pending_delivery_logs(announcement)
        return Response(self.get_serializer(announcement).data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
        url_path='dispatch',
        url_name='dispatch',
    )
    def dispatch_push(self, request, pk=None):
        announcement = self.get_object()
        self.create_pending_delivery_logs(announcement)
        result = PushNotificationService().dispatch_pending_for_announcement(announcement)
        return Response(
            {
                'detail': 'Delivery dispatch processed.',
                'provider_configured': result['configured'],
                'sent': result['sent'],
                'failed': result['failed'],
                'pending': result['pending'],
                'total_logs': announcement.delivery_logs.count(),
            }
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request, pk=None):
        announcement = self.get_object()
        logs = announcement.delivery_logs.all()
        failed_logs = logs.filter(status=DeliveryLog.STATUS_FAILED)
        return Response(
            {
                'announcement': announcement.id,
                'pending': logs.filter(status=DeliveryLog.STATUS_PENDING).count(),
                'sent': logs.filter(status=DeliveryLog.STATUS_SENT).count(),
                'failed': failed_logs.count(),
                'viewed': logs.filter(status=DeliveryLog.STATUS_VIEWED).count(),
                'total': logs.count(),
                'failed_errors': [
                    {
                        'log_id': log.id,
                        'device_id': log.device_id,
                        'error_message': log.error_message,
                    }
                    for log in failed_logs.select_related('device')
                ],
            }
        )


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.select_related('announcement').all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsManagerOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get('file')
        if uploaded_file:
            validate_attachment(uploaded_file)
            serializer.save(
                original_name=uploaded_file.name,
                file_type=attachment_type(uploaded_file),
            )
        else:
            serializer.save()


class PushDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = PushDeviceSerializer
    parser_classes = [parsers.JSONParser, parsers.FormParser]

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
            return Response({'detail': 'token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        defaults = {
            'platform': request.data.get('platform', PushDevice.PLATFORM_WEB),
            'is_active': True,
        }
        if request.user.is_authenticated:
            defaults['user'] = request.user

        device, _ = PushDevice.objects.update_or_create(token=token, defaults=defaults)
        serializer = self.get_serializer(device)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeliveryLogViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return DeliveryLog.objects.select_related(
            'announcement',
            'device',
            'recipient_user',
        ).all()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_viewed(self, request, pk=None):
        log = self.get_object()
        if not request.user.is_staff and log.recipient_user_id != request.user.id:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        log.status = DeliveryLog.STATUS_VIEWED
        log.viewed_at = timezone.now()
        log.save(update_fields=['status', 'viewed_at'])
        return Response(self.get_serializer(log).data)
