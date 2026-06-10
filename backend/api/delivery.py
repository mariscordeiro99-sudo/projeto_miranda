import logging

from django.conf import settings
from django.db.models import Q

from .models import DeliveryLog, PushDevice
from .services import PushNotificationService


logger = logging.getLogger(__name__)


def get_delivery_devices(announcement):
    queryset = PushDevice.objects.filter(is_active=True).select_related('user')
    segment_ids = list(
        announcement.segments
        .filter(is_active=True)
        .values_list('id', flat=True)
    )
    if not segment_ids:
        return queryset

    return (
        queryset
        .filter(
            Q(segments__id__in=segment_ids)
            | Q(user__segments__id__in=segment_ids)
        )
        .distinct()
    )


def create_pending_delivery_logs(announcement):
    devices = list(get_delivery_devices(announcement))
    device_ids = [device.id for device in devices]
    existing_device_ids = set(
        DeliveryLog.objects
        .filter(announcement=announcement, device_id__in=device_ids)
        .values_list('device_id', flat=True)
    )
    logs = [
        DeliveryLog(
            announcement=announcement,
            device=device,
            recipient_user=device.user,
            status=DeliveryLog.STATUS_PENDING,
        )
        for device in devices
        if device.id not in existing_device_ids
    ]
    DeliveryLog.objects.bulk_create(logs, ignore_conflicts=True)


def dispatch_published_announcement(announcement):
    create_pending_delivery_logs(announcement)
    if not getattr(settings, 'PUSH_DISPATCH_ON_PUBLISH', True):
        return {
            'configured': False,
            'sent': 0,
            'failed': 0,
            'pending': announcement.delivery_logs.filter(
                status=DeliveryLog.STATUS_PENDING,
            ).count(),
            'skipped': True,
        }

    if getattr(settings, 'PUSH_DISPATCH_ASYNC', False):
        service = PushNotificationService()
        try:
            from .tasks import process_announcement_deliveries

            process_announcement_deliveries.delay(announcement.id)
            return {
                'configured': service.is_configured,
                'sent': 0,
                'failed': 0,
                'pending': announcement.delivery_logs.filter(
                    status=DeliveryLog.STATUS_PENDING,
                ).count(),
                'queued': True,
                'skipped': False,
            }
        except Exception as error:
            logger.exception(
                'Failed to enqueue announcement delivery; falling back to sync dispatch.',
                extra={'announcement_id': announcement.id, 'error': str(error)},
            )

    result = PushNotificationService().dispatch_pending_for_announcement(announcement)
    result['queued'] = False
    result['skipped'] = False
    return result
