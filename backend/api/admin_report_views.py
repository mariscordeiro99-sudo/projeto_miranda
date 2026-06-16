from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse

from .models import Announcement, DeliveryLog, PushDevice


def user_report_row(user, role_label):
    return {
        'url': reverse('admin:auth_user_change', args=[user.id]),
        'primary': user.get_full_name() or user.username,
        'secondary': user.email or 'Sem e-mail',
        'meta': role_label,
        'status': 'Ativo',
    }


@staff_member_required
def active_users_report(request):
    users = User.objects.filter(is_active=True).order_by('username')
    citizens = users.filter(is_staff=False, is_superuser=False)
    administrators = users.filter(is_staff=True)
    groups = [
        {
            'title': 'Usu\u00e1rios cidad\u00e3os ativos',
            'count': citizens.count(),
            'rows': [
                user_report_row(user, 'Cidad\u00e3o')
                for user in citizens
            ],
            'empty_message': 'Nenhum cidad\u00e3o ativo encontrado.',
        },
        {
            'title': 'Administradores ativos',
            'count': administrators.count(),
            'rows': [
                user_report_row(user, 'Administrador')
                for user in administrators
            ],
            'empty_message': 'Nenhum administrador ativo encontrado.',
        },
    ]
    return render_report(
        request,
        title='Usu\u00e1rios ativos',
        eyebrow='Relat\u00f3rio de acesso',
        count=users.count(),
        rows=[],
        groups=groups,
        empty_message='Nenhum usu\u00e1rio ativo encontrado.',
    )


@staff_member_required
def published_announcements_report(request):
    announcements = (
        Announcement.objects
        .filter(status=Announcement.STATUS_PUBLISHED)
        .select_related('author', 'institution')
        .order_by('-published_at', '-created_at')
    )
    rows = [
        {
            'url': reverse('admin:api_announcement_change', args=[announcement.id]),
            'primary': announcement.title,
            'secondary': announcement.author.get_username() if announcement.author else 'Sem autor',
            'meta': announcement.published_at or announcement.created_at,
            'status': 'Publicado',
        }
        for announcement in announcements
    ]
    return render_report(
        request,
        title='Comunicados publicados',
        eyebrow='Conteúdo oficial',
        count=announcements.count(),
        rows=rows,
        empty_message='Nenhum comunicado publicado encontrado.',
    )


@staff_member_required
def active_devices_report(request):
    devices = (
        PushDevice.objects
        .filter(is_active=True)
        .select_related('user')
        .order_by('-updated_at')
    )
    rows = [
        {
            'url': reverse('admin:api_pushdevice_change', args=[device.id]),
            'primary': device.user.get_username() if device.user else 'Sem usuário',
            'secondary': f'{device.platform} #{device.id}',
            'meta': token_preview(device.token),
            'status': 'Ativo',
        }
        for device in devices
    ]
    return render_report(
        request,
        title='Dispositivos ativos',
        eyebrow='Notificações push',
        count=devices.count(),
        rows=rows,
        empty_message='Nenhum dispositivo ativo encontrado.',
    )


@staff_member_required
def failed_deliveries_report(request):
    logs = (
        DeliveryLog.objects
        .filter(status=DeliveryLog.STATUS_FAILED)
        .select_related('announcement', 'device', 'recipient_user')
        .order_by('-created_at')
    )
    rows = [
        {
            'url': reverse('admin:api_deliverylog_change', args=[log.id]),
            'primary': log.announcement.title if log.announcement else 'Sem comunicado',
            'secondary': log.error_message or 'Falha sem mensagem registrada',
            'meta': log.device.platform if log.device else 'Sem dispositivo',
            'status': 'Falhou',
        }
        for log in logs
    ]
    return render_report(
        request,
        title='Falhas de envio',
        eyebrow='Logs de entrega',
        count=logs.count(),
        rows=rows,
        empty_message='Nenhuma falha de envio encontrada.',
        danger=True,
    )


def render_report(request, title, eyebrow, count, rows, empty_message, danger=False, groups=None):
    return render(
        request,
        'admin/reports/detail.html',
        {
            **admin_context(request),
            'title': title,
            'eyebrow': eyebrow,
            'count': count,
            'rows': rows,
            'groups': groups or [],
            'empty_message': empty_message,
            'danger': danger,
            'dashboard_url': reverse('admin:index'),
        },
    )


def admin_context(request):
    return {
        'site_header': 'Administração do Projeto Miranda',
        'site_title': 'Projeto Miranda',
        'has_permission': True,
        'is_popup': False,
        'is_nav_sidebar_enabled': False,
        'user': request.user,
    }


def token_preview(token):
    if not token:
        return ''
    if len(token) <= 12:
        return token
    return f'{token[:12]}...'
