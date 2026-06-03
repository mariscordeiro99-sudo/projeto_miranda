from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse

from .models import Announcement, DeliveryLog, PushDevice


@staff_member_required
def active_users_report(request):
    users = User.objects.filter(is_active=True).order_by('username')
    rows = [
        {
            'url': reverse('admin:auth_user_change', args=[user.id]),
            'primary': user.get_full_name() or user.username,
            'secondary': user.email or 'Sem e-mail',
            'meta': 'Staff' if user.is_staff else 'Cidadao',
            'status': 'Ativo',
        }
        for user in users
    ]
    return render_report(
        request,
        title='Usuarios ativos',
        eyebrow='Relatorio de acesso',
        count=users.count(),
        rows=rows,
        empty_message='Nenhum usuario ativo encontrado.',
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
        eyebrow='Conteudo oficial',
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
            'primary': device.user.get_username() if device.user else 'Sem usuario',
            'secondary': f'{device.platform} #{device.id}',
            'meta': token_preview(device.token),
            'status': 'Ativo',
        }
        for device in devices
    ]
    return render_report(
        request,
        title='Dispositivos ativos',
        eyebrow='Push notification',
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


def render_report(request, title, eyebrow, count, rows, empty_message, danger=False):
    return render(
        request,
        'admin/reports/detail.html',
        {
            **admin_context(request),
            'title': title,
            'eyebrow': eyebrow,
            'count': count,
            'rows': rows,
            'empty_message': empty_message,
            'danger': danger,
            'dashboard_url': reverse('admin:index'),
        },
    )


def admin_context(request):
    return {
        'site_header': 'Administracao do Projeto Miranda',
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
