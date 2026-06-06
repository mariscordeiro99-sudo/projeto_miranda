# Generated manually to make delivery view metrics reliable.

from django.db import migrations, models


STATUS_PRIORITY = {
    'viewed': 4,
    'sent': 3,
    'failed': 2,
    'pending': 1,
}


def deduplicate_delivery_logs(apps, schema_editor):
    DeliveryLog = apps.get_model('api', 'DeliveryLog')

    duplicate_groups = (
        DeliveryLog.objects
        .exclude(device_id__isnull=True)
        .values('announcement_id', 'device_id')
        .annotate(total=models.Count('id'))
        .filter(total__gt=1)
    )

    for group in duplicate_groups:
        logs = list(
            DeliveryLog.objects
            .filter(
                announcement_id=group['announcement_id'],
                device_id=group['device_id'],
            )
            .order_by('created_at', 'id')
        )
        keep = max(
            logs,
            key=lambda log: (
                STATUS_PRIORITY.get(log.status, 0),
                log.viewed_at or log.sent_at or log.created_at,
                log.id,
            ),
        )
        keep.viewed_at = max(
            [log.viewed_at for log in logs if log.viewed_at],
            default=keep.viewed_at,
        )
        keep.sent_at = max(
            [log.sent_at for log in logs if log.sent_at],
            default=keep.sent_at,
        )
        failed_messages = [log.error_message for log in logs if log.error_message]
        if failed_messages and not keep.error_message:
            keep.error_message = failed_messages[-1]
        keep.save(update_fields=['status', 'viewed_at', 'sent_at', 'error_message'])

        delete_ids = [log.id for log in logs if log.id != keep.id]
        DeliveryLog.objects.filter(id__in=delete_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_announcement_options_alter_attachment_options_and_more'),
    ]

    operations = [
        migrations.RunPython(deduplicate_delivery_logs, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='deliverylog',
            constraint=models.UniqueConstraint(
                fields=('announcement', 'device'),
                name='unique_delivery_log_per_device',
            ),
        ),
    ]
