from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from .backup import record_backup_operational_evidence as record_backup_evidence
from .delivery import create_pending_delivery_logs
from .models import Announcement, DeliveryLog, PushDevice
from .services import PushNotificationService, mark_failed_delivery


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_announcement_deliveries(self, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    create_pending_delivery_logs(announcement)
    return PushNotificationService().dispatch_pending_for_announcement(announcement)


@shared_task
def retry_failed_deliveries(hours=1):
    cutoff = timezone.now() - timedelta(hours=hours)
    logs = (
        DeliveryLog.objects
        .filter(status=DeliveryLog.STATUS_FAILED, created_at__lte=cutoff)
        .select_related('announcement')
    )
    announcement_ids = list(
        logs.values_list('announcement_id', flat=True).distinct()
    )
    updated = logs.update(
        status=DeliveryLog.STATUS_PENDING,
        error_message='',
        sent_at=None,
    )

    dispatched = {}
    for announcement_id in announcement_ids:
        announcement = Announcement.objects.get(id=announcement_id)
        dispatched[announcement_id] = PushNotificationService().dispatch_pending_for_announcement(
            announcement
        )

    return {
        'reset_to_pending': updated,
        'announcements': dispatched,
    }


@shared_task
def cleanup_old_delivery_logs(days=90):
    cutoff = timezone.now() - timedelta(days=days)
    deleted_count, _ = DeliveryLog.objects.filter(created_at__lt=cutoff).delete()
    return {'deleted': deleted_count}


@shared_task
def mark_stale_deliveries_as_failed(hours=24):
    cutoff = timezone.now() - timedelta(hours=hours)
    stale_logs = DeliveryLog.objects.filter(
        status=DeliveryLog.STATUS_PENDING,
        created_at__lt=cutoff,
    )
    total = stale_logs.count()
    for log in stale_logs.iterator():
        mark_failed_delivery(log, 'Entrega permaneceu pendente além do prazo permitido.')
    return {'failed': total}


@shared_task
def deactivate_invalid_push_devices():
    invalid_messages = PushNotificationService.INVALID_TOKEN_MESSAGES
    logs = DeliveryLog.objects.filter(status=DeliveryLog.STATUS_FAILED).exclude(device=None)

    device_ids = set()
    for invalid_message in invalid_messages:
        device_ids.update(
            logs.filter(error_message__icontains=invalid_message).values_list(
                'device_id',
                flat=True,
            )
        )

    updated = PushDevice.objects.filter(id__in=device_ids, is_active=True).update(
        is_active=False,
        updated_at=timezone.now(),
    )
    return {'deactivated': updated}


@shared_task
def record_backup_operational_evidence():
    return record_backup_evidence()


@shared_task
def generate_delivery_report(announcement_id=None):
    logs = DeliveryLog.objects.all()
    if announcement_id:
        logs = logs.filter(announcement_id=announcement_id)

    status_counts = {
        status_name: 0
        for status_name, _ in DeliveryLog.STATUS_CHOICES
    }
    status_counts.update({
        row['status']: row['total']
        for row in logs.values('status').annotate(total=Count('id'))
    })

    return {
        'announcement_id': announcement_id,
        'total': logs.count(),
        'by_status': status_counts,
        'generated_at': timezone.now().isoformat(),
        'environment': 'development' if settings.DEBUG else 'production',
    }
