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
        (ROLE_CITIZEN, 'Cidadao'),
        (ROLE_MANAGER, 'Gestor'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone_number = models.CharField(max_length=20, blank=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CITIZEN)
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
        (KIND_COUNCIL, 'Camara'),
    ]

    name = models.CharField(max_length=180)
    kind = models.CharField(max_length=30, choices=KIND_CHOICES, default=KIND_CITY_HALL)
    official_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Instituicao'
        verbose_name_plural = 'Instituicoes'

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
        (TYPE_VIDEO, 'Video'),
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
        (CHANNEL_PUSH, 'Notificacao push'),
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
        indexes = [
            models.Index(fields=['announcement', 'status']),
            models.Index(fields=['recipient_user', 'created_at']),
        ]

    def __str__(self):
        return f'{self.announcement_id} - {self.status}'
