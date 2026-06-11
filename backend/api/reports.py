from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count, Q

from .models import Announcement, DeliveryLog, Profile, PushDevice


def get_cached_dashboard_report(include_activity=True):
    cache_key = (
        'dashboard-report:full:v2'
        if include_activity
        else 'dashboard-report:admin:v2'
    )
    cached_report = cache.get(cache_key)
    if cached_report is not None:
        return cached_report

    report = build_dashboard_report(include_activity=include_activity)
    cache.set(
        cache_key,
        report,
        getattr(settings, 'DASHBOARD_REPORT_CACHE_TIMEOUT', 30),
    )
    return report


def clear_dashboard_report_cache():
    cache.delete_many([
        'dashboard-report:full:v2',
        'dashboard-report:admin:v2',
    ])


def build_dashboard_report(include_activity=True):
    delivery = build_delivery_metrics()
    report = {
        'users': build_user_metrics(),
        'announcements': build_announcement_metrics(),
        'delivery': delivery,
        'devices': build_device_metrics(),
        'recent_announcements': build_recent_announcement_metrics(),
        'recent_failures': build_recent_failure_details(),
    }

    if include_activity:
        report['active_devices'] = build_active_device_details()
        report['recent_views'] = build_recent_view_details()
    else:
        report['active_devices'] = []
        report['recent_views'] = []

    return report


def build_delivery_metrics():
    metrics = DeliveryLog.objects.aggregate(
        total_logs=Count('id'),
        pending=Count('id', filter=Q(status=DeliveryLog.STATUS_PENDING)),
        sent=Count(
            'id',
            filter=Q(status__in=[
                DeliveryLog.STATUS_SENT,
                DeliveryLog.STATUS_VIEWED,
            ]),
        ),
        failed=Count('id', filter=Q(status=DeliveryLog.STATUS_FAILED)),
        viewed=Count('id', filter=Q(status=DeliveryLog.STATUS_VIEWED)),
    )
    total_logs = metrics['total_logs']

    return {
        **metrics,
        'view_rate': percentage(metrics['viewed'], total_logs),
        'failure_rate': percentage(metrics['failed'], total_logs),
    }


def build_user_metrics():
    user_metrics = User.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True)),
        staff=Count('id', filter=Q(is_staff=True)),
    )
    profile_metrics = Profile.objects.aggregate(
        citizens=Count('id', filter=Q(role=Profile.ROLE_CITIZEN)),
        managers=Count('id', filter=Q(role=Profile.ROLE_MANAGER)),
    )

    return {
        **user_metrics,
        **profile_metrics,
        'with_active_push_device': (
            PushDevice.objects
            .filter(is_active=True, user_id__isnull=False)
            .values('user_id')
            .distinct()
            .count()
        ),
    }


def build_announcement_metrics():
    return Announcement.objects.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(status=Announcement.STATUS_PUBLISHED)),
        draft=Count('id', filter=Q(status=Announcement.STATUS_DRAFT)),
        archived=Count('id', filter=Q(status=Announcement.STATUS_ARCHIVED)),
        pinned=Count('id', filter=Q(pinned=True)),
    )


def build_device_metrics():
    platform_counts = {
        platform: 0
        for platform, _ in PushDevice.PLATFORM_CHOICES
    }
    platform_counts.update({
        row['platform']: row['total']
        for row in PushDevice.objects.values('platform').annotate(total=Count('id'))
    })
    device_metrics = PushDevice.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_active=True)),
        inactive=Count('id', filter=Q(is_active=False)),
        anonymous=Count('id', filter=Q(user_id__isnull=True)),
        active_mobile=Count(
            'id',
            filter=Q(
                is_active=True,
                platform__in=[
                    PushDevice.PLATFORM_ANDROID,
                    PushDevice.PLATFORM_IOS,
                ],
            ),
        ),
        active_web=Count(
            'id',
            filter=Q(is_active=True, platform=PushDevice.PLATFORM_WEB),
        ),
    )

    return {
        **device_metrics,
        'by_platform': platform_counts,
    }


def build_recent_announcement_metrics():
    recent_ids = list(
        Announcement.objects
        .order_by('-created_at')
        .values_list('id', flat=True)[:5]
    )
    if not recent_ids:
        return []

    announcements = (
        Announcement.objects
        .filter(id__in=recent_ids)
        .annotate(
            delivery_total=Count('delivery_logs'),
            viewed_total=Count(
                'delivery_logs',
                filter=Q(delivery_logs__status=DeliveryLog.STATUS_VIEWED),
            ),
            sent_total=Count(
                'delivery_logs',
                filter=Q(
                    delivery_logs__status__in=[
                        DeliveryLog.STATUS_SENT,
                        DeliveryLog.STATUS_VIEWED,
                    ]
                ),
            ),
            failed_total=Count(
                'delivery_logs',
                filter=Q(delivery_logs__status=DeliveryLog.STATUS_FAILED),
            ),
        )
        .order_by('-created_at')
    )

    return [
        {
            'id': announcement.id,
            'title': announcement.title,
            'status': announcement.status,
            'published_at': announcement.published_at,
            'created_at': announcement.created_at,
            'delivery_total': announcement.delivery_total,
            'sent': announcement.sent_total,
            'failed': announcement.failed_total,
            'viewed': announcement.viewed_total,
            'view_rate': percentage(
                announcement.viewed_total,
                announcement.delivery_total,
            ),
        }
        for announcement in announcements
    ]


def build_active_device_details(limit=5):
    devices = (
        PushDevice.objects
        .filter(is_active=True)
        .select_related('user')
        .order_by('-updated_at')[:limit]
    )

    return [
        {
            'id': device.id,
            'platform': device.platform,
            'user': user_label(device.user),
            'token_preview': token_preview(device.token),
            'updated_at': device.updated_at,
        }
        for device in devices
    ]


def build_recent_failure_details(limit=3):
    logs = (
        DeliveryLog.objects
        .filter(status=DeliveryLog.STATUS_FAILED)
        .select_related('announcement', 'device', 'recipient_user')
        .order_by('-created_at')[:limit]
    )

    return [
        {
            'id': log.id,
            'announcement': announcement_label(log.announcement),
            'device': device_label(log.device),
            'recipient': user_label(log.recipient_user),
            'error_message': truncate(log.error_message, 160),
            'created_at': log.created_at,
        }
        for log in logs
    ]


def build_recent_view_details(limit=5):
    logs = (
        DeliveryLog.objects
        .filter(status=DeliveryLog.STATUS_VIEWED)
        .select_related('announcement', 'device', 'recipient_user')
        .order_by('-viewed_at', '-created_at')[:limit]
    )

    return [
        {
            'id': log.id,
            'announcement': announcement_label(log.announcement),
            'device': device_label(log.device),
            'recipient': user_label(log.recipient_user),
            'recipient_initials': user_initials(log.recipient_user),
            'viewed_at': log.viewed_at,
        }
        for log in logs
    ]


def announcement_label(announcement):
    if not announcement:
        return 'Sem comunicado'
    return announcement.title


def device_label(device):
    if not device:
        return 'Sem dispositivo'
    return f'{device.platform} #{device.id}'


def user_label(user):
    if not user:
        return 'Sem usuário'
    return user.get_full_name() or user.username


def user_initials(user):
    if not user:
        return '--'

    names = (user.get_full_name() or user.username).split()
    initials = ''.join(name[:1].upper() for name in names[:2])
    return initials or '--'


def token_preview(token):
    if not token:
        return ''
    if len(token) <= 12:
        return token
    return f'{token[:12]}...'


def truncate(value, max_length):
    value = value or ''
    if len(value) <= max_length:
        return value
    return f'{value[:max_length - 3]}...'


def percentage(numerator, denominator):
    if not denominator:
        return 0.0
    return round((numerator / denominator) * 100, 2)
