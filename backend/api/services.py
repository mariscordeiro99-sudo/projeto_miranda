from django.conf import settings
from django.utils import timezone

from .models import DeliveryLog

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except ImportError:  # pragma: no cover - dependency may be absent locally before install
    firebase_admin = None
    credentials = None
    messaging = None


class PushNotificationService:
    def __init__(self):
        self.enabled = getattr(settings, 'FIREBASE_ENABLED', False)
        self.project_id = getattr(settings, 'FIREBASE_PROJECT_ID', '')
        self.client_email = getattr(settings, 'FIREBASE_CLIENT_EMAIL', '')
        self.private_key = getattr(settings, 'FIREBASE_PRIVATE_KEY', '')

    @property
    def is_configured(self):
        return bool(
            self.enabled
            and firebase_admin
            and self.project_id
            and self.client_email
            and self.private_key
        )

    def get_app(self):
        if firebase_admin._apps:
            return firebase_admin.get_app()

        private_key = self.private_key.replace('\\n', '\n')
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
        for log in logs.select_related('device', 'announcement'):
            if not log.device or not log.device.is_active:
                self.mark_failed(log, 'Device is inactive or missing.')
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
                        'title': announcement.title,
                    },
                )
                messaging.send(message, app=app)
            except Exception as error:
                self.mark_failed(log, str(error))
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


class HttpPushNotificationService:
    def __init__(self):
        self.provider_url = getattr(settings, 'PUSH_PROVIDER_URL', '')
        self.auth_header = getattr(settings, 'PUSH_PROVIDER_AUTH_HEADER', 'Authorization')
        self.auth_token = getattr(settings, 'PUSH_PROVIDER_AUTH_TOKEN', '')

    @property
    def is_configured(self):
        return bool(self.provider_url and self.auth_token)

    def dispatch_pending_for_announcement(self, announcement):
        import requests

        logs = announcement.delivery_logs.filter(status=DeliveryLog.STATUS_PENDING)
        result = {
            'configured': self.is_configured,
            'sent': 0,
            'failed': 0,
            'pending': logs.count(),
        }

        if not self.is_configured:
            return result

        for log in logs.select_related('device', 'announcement'):
            if not log.device or not log.device.is_active:
                self.mark_failed(log, 'Device is inactive or missing.')
                result['failed'] += 1
                continue

            try:
                response = requests.post(
                    self.provider_url,
                    json={
                        'token': log.device.token,
                        'title': announcement.title,
                        'body': announcement.content,
                        'data': {
                            'announcement_id': announcement.id,
                        },
                    },
                    headers={self.auth_header: self.auth_token},
                    timeout=10,
                )
                response.raise_for_status()
            except requests.RequestException as error:
                self.mark_failed(log, str(error))
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


def mark_failed_delivery(log, message):
    log.status = DeliveryLog.STATUS_FAILED
    log.error_message = message[:1000]
    log.save(update_fields=['status', 'error_message'])
