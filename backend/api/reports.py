from django.contrib.auth.models import User
from django.db.models import Count, Q

from .models import Announcement, DeliveryLog, Profile, PushDevice


def build_dashboard_report():
    delivery_total = DeliveryLog.objects.count()
    delivery_sent = DeliveryLog.objects.filter(
        status__in=[DeliveryLog.STATUS_SENT, DeliveryLog.STATUS_VIEWED]
    ).count()
    delivery_failed = DeliveryLog.objects.filter(status=DeliveryLog.STATUS_FAILED).count()
    delivery_viewed = DeliveryLog.objects.filter(status=DeliveryLog.STATUS_VIEWED).count()

    return {
        'users': build_user_metrics(),
        'announcements': build_announcement_metrics(),
        'delivery': {
            'total_logs': delivery_total,
            'pending': DeliveryLog.objects.filter(status=DeliveryLog.STATUS_PENDING).count(),
            'sent': delivery_sent,
            'failed': delivery_failed,
            'viewed': delivery_viewed,
            'view_rate': percentage(delivery_viewed, delivery_total),
            'failure_rate': percentage(delivery_failed, delivery_total),
        },
        'devices': build_device_metrics(),
        'recent_announcements': build_recent_announcement_metrics(),
    }


def build_user_metrics():
    return {
        'total': User.objects.count(),
        'active': User.objects.filter(is_active=True).count(),
        'staff': User.objects.filter(is_staff=True).count(),
        'citizens': Profile.objects.filter(role=Profile.ROLE_CITIZEN).count(),
        'managers': Profile.objects.filter(role=Profile.ROLE_MANAGER).count(),
        'with_active_push_device': (
            PushDevice.objects
            .filter(is_active=True, user_id__isnull=False)
            .values('user_id')
            .distinct()
            .count()
        ),
    }


def build_announcement_metrics():
    return {
        'total': Announcement.objects.count(),
        'published': Announcement.objects.filter(
            status=Announcement.STATUS_PUBLISHED
        ).count(),
        'draft': Announcement.objects.filter(status=Announcement.STATUS_DRAFT).count(),
        'archived': Announcement.objects.filter(status=Announcement.STATUS_ARCHIVED).count(),
        'pinned': Announcement.objects.filter(pinned=True).count(),
    }


def build_device_metrics():
    platform_counts = {
        platform: 0
        for platform, _ in PushDevice.PLATFORM_CHOICES
    }
    platform_counts.update({
        row['platform']: row['total']
        for row in PushDevice.objects.values('platform').annotate(total=Count('id'))
    })

    return {
        'total': PushDevice.objects.count(),
        'active': PushDevice.objects.filter(is_active=True).count(),
        'inactive': PushDevice.objects.filter(is_active=False).count(),
        'anonymous': PushDevice.objects.filter(user_id__isnull=True).count(),
        'by_platform': platform_counts,
    }


def build_recent_announcement_metrics():
    announcements = (
        Announcement.objects
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
        .order_by('-created_at')[:5]
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


def percentage(numerator, denominator):
    if not denominator:
        return 0.0
    return round((numerator / denominator) * 100, 2)
