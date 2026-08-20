from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class Document(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return self.title


class Profile(models.Model):
    ROLE_CITIZEN = 'citizen'
    ROLE_MANAGER = 'manager'
    ROLE_CHOICES = [
        (ROLE_CITIZEN, 'Cidadão'),
        (ROLE_MANAGER, 'Gestor'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone_number = models.CharField(max_length=20, blank=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CITIZEN)
    manager_access_requested = models.BooleanField(default=False)
    can_control_access = models.BooleanField(default=False)
    can_manage_announcements = models.BooleanField(default=False)
    can_manage_visual_identity = models.BooleanField(default=False)
    can_view_manager_dashboard = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.user.username} ({self.role})'


class Institution(models.Model):
    KIND_CITY_HALL = 'city_hall'
    KIND_COUNCIL = 'council'
    KIND_CHOICES = [
        (KIND_CITY_HALL, 'Prefeitura'),
        (KIND_COUNCIL, 'Câmara'),
    ]

    name = models.CharField(max_length=180)
    kind = models.CharField(max_length=30, choices=KIND_CHOICES, default=KIND_CITY_HALL)
    official_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Instituição'
        verbose_name_plural = 'Instituições'

    def __str__(self):
        return self.name


class VisualIdentity(models.Model):
    hex_color_validator = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='Use uma cor hexadecimal como #123ABC.',
    )

    institution = models.OneToOneField(
        Institution,
        on_delete=models.CASCADE,
        related_name='visual_identity',
    )
    logo = models.ImageField(upload_to='identity/logos/', blank=True, null=True)
    coat_of_arms = models.ImageField(upload_to='identity/coat_of_arms/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, validators=[hex_color_validator], default='#0057A8')
    secondary_color = models.CharField(max_length=7, validators=[hex_color_validator], default='#00A676')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Identidade visual'
        verbose_name_plural = 'Identidades visuais'

    def __str__(self):
        return f'Identidade visual - {self.institution.name}'


class Segment(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='segments',
        blank=True,
    )
    push_devices = models.ManyToManyField(
        'PushDevice',
        related_name='segments',
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Segmento'
        verbose_name_plural = 'Segmentos'
        ordering = ['name']

    def __str__(self):
        return self.name


class Announcement(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Rascunho'),
        (STATUS_PUBLISHED, 'Publicado'),
        (STATUS_ARCHIVED, 'Arquivado'),
    ]

    institution = models.ForeignKey(
        Institution,
        on_delete=models.SET_NULL,
        related_name='announcements',
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='announcements',
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=180)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    segments = models.ManyToManyField(
        Segment,
        related_name='announcements',
        blank=True,
    )
    pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comunicado'
        verbose_name_plural = 'Comunicados'
        ordering = ['-pinned', '-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['pinned', 'published_at']),
        ]

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Attachment(models.Model):
    TYPE_DOCUMENT = 'document'
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = [
        (TYPE_DOCUMENT, 'Documento'),
        (TYPE_IMAGE, 'Imagem'),
        (TYPE_VIDEO, 'Vídeo'),
        (TYPE_OTHER, 'Outro'),
    ]

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(upload_to='announcements/%Y/%m/')
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_OTHER)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anexo'
        verbose_name_plural = 'Anexos'

    def __str__(self):
        return self.original_name


class PushDevice(models.Model):
    PLATFORM_ANDROID = 'android'
    PLATFORM_IOS = 'ios'
    PLATFORM_WEB = 'web'
    PLATFORM_CHOICES = [
        (PLATFORM_ANDROID, 'Android'),
        (PLATFORM_IOS, 'iOS'),
        (PLATFORM_WEB, 'Web'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='push_devices',
        blank=True,
        null=True,
    )
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default=PLATFORM_WEB)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dispositivo push'
        verbose_name_plural = 'Dispositivos push'

    def __str__(self):
        return f'{self.platform} - {self.token[:12]}'


class DeliveryLog(models.Model):
    CHANNEL_PUSH = 'push'
    CHANNEL_CHOICES = [
        (CHANNEL_PUSH, 'Notificação push'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_VIEWED = 'viewed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_SENT, 'Enviado'),
        (STATUS_FAILED, 'Falhou'),
        (STATUS_VIEWED, 'Visualizado'),
    ]

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='delivery_logs',
    )
    device = models.ForeignKey(
        PushDevice,
        on_delete=models.SET_NULL,
        related_name='delivery_logs',
        blank=True,
        null=True,
    )
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='delivery_logs',
        blank=True,
        null=True,
    )
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_PUSH)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    viewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de entrega'
        verbose_name_plural = 'Logs de entrega'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['announcement', 'device'],
                name='unique_delivery_log_per_device',
            ),
        ]
        indexes = [
            models.Index(fields=['announcement', 'status']),
            models.Index(fields=['recipient_user', 'created_at']),
        ]

    def __str__(self):
        return f'{self.announcement_id} - {self.status}'


class ChatMessage(models.Model):
    TYPE_TEXT = 'texto'
    TYPE_AUDIO = 'audio'
    TYPE_IMAGE = 'imagem'
    TYPE_VIDEO = 'video'
    TYPE_DOCUMENT = 'documento'
    TYPE_CHOICES = [
        (TYPE_TEXT, 'Texto'),
        (TYPE_AUDIO, 'Áudio'),
        (TYPE_IMAGE, 'Imagem'),
        (TYPE_VIDEO, 'Vídeo'),
        (TYPE_DOCUMENT, 'Documento'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_chat_messages',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_chat_messages',
    )
    text = models.TextField(blank=True)
    message_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_TEXT,
    )
    file = models.FileField(upload_to='chat/%Y/%m/', blank=True, null=True)
    original_name = models.CharField(max_length=255, blank=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensagem de chat'
        verbose_name_plural = 'Mensagens de chat'
        ordering = ['created_at']
        indexes = [
            models.Index(
                fields=['sender', 'receiver', 'created_at'],
                name='api_chatmes_sender__051465_idx',
            ),
            models.Index(
                fields=['receiver', 'read_at'],
                name='api_chatmes_receive_7ba4a8_idx',
            ),
        ]

    def __str__(self):
        return f'{self.sender_id} -> {self.receiver_id} ({self.message_type})'


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        blank=True,
        null=True,
    )
    actor_username = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=80, db_index=True)
    target_type = models.CharField(max_length=80, blank=True, db_index=True)
    target_id = models.CharField(max_length=80, blank=True, db_index=True)
    target_repr = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de auditoria'
        verbose_name_plural = 'Logs de auditoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def __str__(self):
        actor = self.actor_username or 'sistema'
        return f'{self.created_at:%Y-%m-%d %H:%M} - {actor} - {self.action}'


class PrivacyRequest(models.Model):
    TYPE_ERASURE = 'erasure'
    TYPE_EXPORT = 'export'
    TYPE_DEACTIVATION = 'deactivation'
    TYPE_CHOICES = [
        (TYPE_ERASURE, 'Exclusão de dados'),
        (TYPE_EXPORT, 'Exportação de dados'),
        (TYPE_DEACTIVATION, 'Desativação de conta'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_COMPLETED, 'Concluída'),
        (STATUS_REJECTED, 'Rejeitada'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='privacy_requests',
        blank=True,
        null=True,
    )
    requester_name = models.CharField(max_length=180, blank=True)
    requester_email = models.EmailField(blank=True)
    request_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_ERASURE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='resolved_privacy_requests',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Solicitação LGPD'
        verbose_name_plural = 'Solicitações LGPD'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['request_type', 'created_at']),
        ]

    def __str__(self):
        return f'{self.request_type} - {self.requester_email or self.requester_name}'
