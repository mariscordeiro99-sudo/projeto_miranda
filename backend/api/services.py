from django.conf import settings
from django.utils import timezone

from .models import DeliveryLog

_firebase_modules = None


def normalize_firebase_private_key(private_key):
    private_key = (private_key or '').strip()
    private_key = private_key.strip('"').strip("'")
    return private_key.replace('\\n', '\n').strip()


class PushNotificationService:
    INVALID_TOKEN_MESSAGES = (
        'not a valid FCM registration token',
        'registration token is not a valid',
        'requested entity was not found',
        'registration-token-not-registered',
        'unregistered',
    )

    def __init__(self):
        self.enabled = getattr(settings, 'FIREBASE_ENABLED', False)
        self.project_id = getattr(settings, 'FIREBASE_PROJECT_ID', '')
        self.client_email = getattr(settings, 'FIREBASE_CLIENT_EMAIL', '')
        self.private_key = getattr(settings, 'FIREBASE_PRIVATE_KEY', '')

    @property
    def is_configured(self):
        return bool(
            self.enabled
            and self.firebase_modules[0]
            and self.project_id
            and self.client_email
            and self.private_key
        )

    @property
    def firebase_modules(self):
        global _firebase_modules
        if _firebase_modules is not None:
            return _firebase_modules

        if not self.enabled:
            return (None, None, None)

        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
        except ImportError:  # pragma: no cover - dependency may be absent locally before install
            _firebase_modules = (None, None, None)
            return _firebase_modules

        _firebase_modules = (firebase_admin, credentials, messaging)
        return _firebase_modules

    def get_app(self):
        firebase_admin, credentials, _ = self.firebase_modules
        if firebase_admin._apps:
            return firebase_admin.get_app()

        private_key = normalize_firebase_private_key(self.private_key)
        cert = credentials.Certificate(
            {
                'type': 'service_account',
                'project_id': self.project_id,
                'private_key': private_key,
                'client_email': self.client_email,
                'token_uri': 'https://oauth2.googleapis.com/token',
            }
        )
        return firebase_admin.initialize_app(cert)

    def dispatch_pending_for_announcement(self, announcement):
        logs = announcement.delivery_logs.filter(status=DeliveryLog.STATUS_PENDING)
        result = {
            'configured': self.is_configured,
            'sent': 0,
            'failed': 0,
            'pending': logs.count(),
        }

        if not self.is_configured:
            return result

        app = self.get_app()
        _, _, messaging = self.firebase_modules
        for log in logs.select_related('device', 'announcement'):
            if not log.device or not log.device.is_active:
                self.mark_failed(log, 'Dispositivo ausente ou inativo.')
                result['failed'] += 1
                continue

            try:
                message = messaging.Message(
                    token=log.device.token,
                    notification=messaging.Notification(
                        title=announcement.title,
                        body=announcement.content[:240],
                    ),
                    data={
                        'announcement_id': str(announcement.id),
                        'delivery_log_id': str(log.id),
                        'title': announcement.title,
                    },
                )
                messaging.send(message, app=app)
            except Exception as error:
                message = str(error)
                if self.is_invalid_token_error(message):
                    self.deactivate_device(log.device)
                self.mark_failed(log, message)
                result['failed'] += 1
                continue

            log.status = DeliveryLog.STATUS_SENT
            log.sent_at = timezone.now()
            log.error_message = ''
            log.save(update_fields=['status', 'sent_at', 'error_message'])
            result['sent'] += 1

        result['pending'] = announcement.delivery_logs.filter(status=DeliveryLog.STATUS_PENDING).count()
        return result

    def mark_failed(self, log, message):
        mark_failed_delivery(log, message)

    def is_invalid_token_error(self, message):
        normalized_message = message.lower()
        return any(error_message.lower() in normalized_message for error_message in self.INVALID_TOKEN_MESSAGES)

    def deactivate_device(self, device):
        if device and device.is_active:
            device.is_active = False
            device.save(update_fields=['is_active', 'updated_at'])


def mark_failed_delivery(log, message):
    log.status = DeliveryLog.STATUS_FAILED
    log.error_message = message[:1000]
    log.save(update_fields=['status', 'error_message'])
