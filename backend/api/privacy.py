from uuid import uuid4

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from .models import (
    Announcement,
    AuditLog,
    DeliveryLog,
    PrivacyRequest,
    Profile,
    PushDevice,
)


ANONYMIZED_REQUESTER_NAME = 'Titular anonimizado'


def process_privacy_request(privacy_request, resolved_by, notes=None):
    with transaction.atomic():
        privacy_request = (
            PrivacyRequest.objects
            .select_for_update()
            .select_related('user', 'resolved_by')
            .get(pk=privacy_request.pk)
        )

        if privacy_request.status != PrivacyRequest.STATUS_PENDING:
            raise ValidationError({'detail': 'Esta solicitação LGPD já foi resolvida.'})

        if privacy_request.request_type == PrivacyRequest.TYPE_EXPORT:
            _mark_request_completed(privacy_request, resolved_by, notes)
            privacy_request.refresh_from_db()
            export_data = build_user_data_export(privacy_request)
            return privacy_request, {
                'action': 'export',
                'export': export_data,
                'summary': {
                    'records_exported': _count_export_records(export_data),
                },
            }

        user = _get_target_user(privacy_request)

        if privacy_request.request_type == PrivacyRequest.TYPE_DEACTIVATION:
            summary = deactivate_user_account(user)
            _mark_request_completed(privacy_request, resolved_by, notes)
            privacy_request.refresh_from_db()
            return privacy_request, {
                'action': 'deactivation',
                'summary': summary,
            }

        if privacy_request.request_type == PrivacyRequest.TYPE_ERASURE:
            summary = anonymize_user_data(user, privacy_request.pk)
            privacy_request.user = None
            privacy_request.requester_name = ANONYMIZED_REQUESTER_NAME
            privacy_request.requester_email = ''
            _mark_request_completed(
                privacy_request,
                resolved_by,
                notes,
                extra_fields=['user', 'requester_name', 'requester_email'],
            )
            privacy_request.refresh_from_db()
            return privacy_request, {
                'action': 'erasure',
                'summary': summary,
            }

        raise ValidationError({'request_type': 'Tipo de solicitação LGPD inválido.'})


def build_user_data_export(privacy_request):
    user = _get_target_user(privacy_request)
    profile = _get_profile(user)
    devices = list(PushDevice.objects.filter(user=user).order_by('id'))
    device_ids = [device.id for device in devices]
    privacy_request_filter = Q(user=user)
    if user.email:
        privacy_request_filter |= Q(requester_email__iexact=user.email)
    privacy_requests = list(
        PrivacyRequest.objects
        .filter(privacy_request_filter)
        .order_by('created_at', 'id')
    )
    privacy_request_ids = [str(item.id) for item in privacy_requests]

    delivery_logs = (
        DeliveryLog.objects
        .filter(Q(recipient_user=user) | Q(device_id__in=device_ids))
        .select_related('announcement', 'device')
        .order_by('created_at', 'id')
    )
    audit_logs = (
        AuditLog.objects
        .filter(
            Q(actor=user)
            | Q(target_type='User', target_id=str(user.id))
            | Q(target_type='PrivacyRequest', target_id__in=privacy_request_ids)
        )
        .order_by('created_at', 'id')
    )
    announcements = (
        Announcement.objects
        .filter(author=user)
        .order_by('created_at', 'id')
    )

    return {
        'generated_at': _serialize_datetime(timezone.now()),
        'privacy_request': {
            'id': privacy_request.id,
            'request_type': privacy_request.request_type,
            'status': privacy_request.status,
            'created_at': _serialize_datetime(privacy_request.created_at),
            'resolved_at': _serialize_datetime(privacy_request.resolved_at),
        },
        'user': _serialize_user(user),
        'profile': _serialize_profile(profile),
        'segments': [
            {
                'id': segment.id,
                'name': segment.name,
                'slug': segment.slug,
                'description': segment.description,
            }
            for segment in user.segments.order_by('name')
        ],
        'push_devices': [_serialize_device(device) for device in devices],
        'delivery_logs': [_serialize_delivery_log(log) for log in delivery_logs],
        'privacy_requests': [
            _serialize_privacy_request(item)
            for item in privacy_requests
        ],
        'audit_logs': [_serialize_audit_log(log) for log in audit_logs],
        'announcements_authored': [
            {
                'id': announcement.id,
                'title': announcement.title,
                'status': announcement.status,
                'published_at': _serialize_datetime(announcement.published_at),
                'created_at': _serialize_datetime(announcement.created_at),
            }
            for announcement in announcements
        ],
        'auth_tokens': {
            'active_count': Token.objects.filter(user=user).count(),
            'tokens_are_not_exported': True,
        },
    }


def anonymize_user_data(user, privacy_request_id=None):
    _ensure_citizen_account(user)

    profile = _get_profile(user)
    device_ids = list(
        PushDevice.objects
        .filter(user=user)
        .order_by('id')
        .values_list('id', flat=True)
    )
    privacy_request_ids = list(
        PrivacyRequest.objects
        .filter(user=user)
        .values_list('id', flat=True)
    )
    if privacy_request_id and privacy_request_id not in privacy_request_ids:
        privacy_request_ids.append(privacy_request_id)

    segments_removed = user.segments.count()
    user.segments.clear()

    tokens_deleted, _ = Token.objects.filter(user=user).delete()

    delivery_logs_updated = (
        DeliveryLog.objects
        .filter(Q(recipient_user=user) | Q(device_id__in=device_ids))
        .update(recipient_user=None, error_message='')
    )

    devices_anonymized = 0
    for device in PushDevice.objects.filter(id__in=device_ids).order_by('id'):
        device.user = None
        device.token = f'erased-device-{device.pk}-{uuid4().hex}'
        device.is_active = False
        device.save(update_fields=['user', 'token', 'is_active', 'updated_at'])
        devices_anonymized += 1

    profile_anonymized = False
    if profile:
        if profile.profile_picture:
            profile.profile_picture.delete(save=False)
        profile.phone_number = ''
        profile.profile_picture = None
        profile.save(update_fields=['phone_number', 'profile_picture', 'updated_at'])
        profile_anonymized = True

    privacy_requests_anonymized = (
        PrivacyRequest.objects
        .filter(id__in=privacy_request_ids)
        .update(
            user=None,
            requester_name=ANONYMIZED_REQUESTER_NAME,
            requester_email='',
        )
    )

    actor_logs_anonymized = (
        AuditLog.objects
        .filter(actor=user)
        .update(actor=None, actor_username='usuario_anonimizado')
    )
    target_logs_anonymized = (
        AuditLog.objects
        .filter(target_type='User', target_id=str(user.id))
        .update(target_repr='Usuário anonimizado', metadata={})
    )
    privacy_logs_anonymized = (
        AuditLog.objects
        .filter(target_type='PrivacyRequest', target_id__in=[str(pk) for pk in privacy_request_ids])
        .update(target_repr='Solicitação LGPD anonimizada')
    )

    Announcement.objects.filter(author=user).update(author=None)

    user.username = f'erased_user_{user.pk}_{uuid4().hex[:8]}'
    user.email = ''
    user.first_name = ''
    user.last_name = ''
    user.is_active = False
    user.set_unusable_password()
    user.save(update_fields=['username', 'email', 'first_name', 'last_name', 'is_active', 'password'])

    return {
        'user_anonymized': True,
        'profile_anonymized': profile_anonymized,
        'tokens_deleted': tokens_deleted,
        'devices_anonymized': devices_anonymized,
        'delivery_logs_anonymized': delivery_logs_updated,
        'segments_removed': segments_removed,
        'privacy_requests_anonymized': privacy_requests_anonymized,
        'audit_logs_anonymized': (
            actor_logs_anonymized
            + target_logs_anonymized
            + privacy_logs_anonymized
        ),
    }


def deactivate_user_account(user):
    _ensure_citizen_account(user)

    user.is_active = False
    user.save(update_fields=['is_active'])
    tokens_deleted, _ = Token.objects.filter(user=user).delete()
    devices_deactivated = PushDevice.objects.filter(user=user).update(is_active=False)

    return {
        'user_deactivated': True,
        'tokens_deleted': tokens_deleted,
        'devices_deactivated': devices_deactivated,
    }


def _mark_request_completed(privacy_request, resolved_by, notes=None, extra_fields=None):
    privacy_request.status = PrivacyRequest.STATUS_COMPLETED
    if notes is not None:
        privacy_request.notes = notes
    privacy_request.resolved_by = resolved_by
    privacy_request.resolved_at = timezone.now()

    update_fields = ['status', 'notes', 'resolved_by', 'resolved_at']
    update_fields.extend(extra_fields or [])
    privacy_request.save(update_fields=update_fields)


def _get_target_user(privacy_request):
    if privacy_request.user_id and privacy_request.user:
        return privacy_request.user
    raise ValidationError({'user': 'A solicitação precisa estar vinculada a um usuário.'})


def _ensure_citizen_account(user):
    if user.is_staff or user.is_superuser:
        raise ValidationError(
            {'detail': 'Contas administrativas exigem tratamento manual de LGPD.'}
        )


def _get_profile(user):
    try:
        return user.profile
    except Profile.DoesNotExist:
        return None


def _count_export_records(export_data):
    record_keys = [
        'segments',
        'push_devices',
        'delivery_logs',
        'privacy_requests',
        'audit_logs',
        'announcements_authored',
    ]
    return sum(len(export_data.get(key, [])) for key in record_keys) + 1


def _serialize_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'date_joined': _serialize_datetime(user.date_joined),
        'last_login': _serialize_datetime(user.last_login),
    }


def _serialize_profile(profile):
    if not profile:
        return None
    return {
        'id': profile.id,
        'phone_number': profile.phone_number,
        'role': profile.role,
        'profile_picture': profile.profile_picture.name if profile.profile_picture else '',
        'created_at': _serialize_datetime(profile.created_at),
        'updated_at': _serialize_datetime(profile.updated_at),
    }


def _serialize_device(device):
    return {
        'id': device.id,
        'token': device.token,
        'platform': device.platform,
        'is_active': device.is_active,
        'created_at': _serialize_datetime(device.created_at),
        'updated_at': _serialize_datetime(device.updated_at),
    }


def _serialize_delivery_log(log):
    return {
        'id': log.id,
        'announcement': {
            'id': log.announcement_id,
            'title': log.announcement.title if log.announcement else '',
        },
        'device_id': log.device_id,
        'recipient_user_id': log.recipient_user_id,
        'channel': log.channel,
        'status': log.status,
        'error_message': log.error_message,
        'sent_at': _serialize_datetime(log.sent_at),
        'viewed_at': _serialize_datetime(log.viewed_at),
        'created_at': _serialize_datetime(log.created_at),
    }


def _serialize_privacy_request(privacy_request):
    return {
        'id': privacy_request.id,
        'request_type': privacy_request.request_type,
        'status': privacy_request.status,
        'requester_name': privacy_request.requester_name,
        'requester_email': privacy_request.requester_email,
        'notes': privacy_request.notes,
        'created_at': _serialize_datetime(privacy_request.created_at),
        'resolved_at': _serialize_datetime(privacy_request.resolved_at),
    }


def _serialize_audit_log(log):
    return {
        'id': log.id,
        'actor_username': log.actor_username,
        'action': log.action,
        'target_type': log.target_type,
        'target_id': log.target_id,
        'target_repr': log.target_repr,
        'metadata': log.metadata,
        'created_at': _serialize_datetime(log.created_at),
    }


def _serialize_datetime(value):
    return value.isoformat() if value else None
