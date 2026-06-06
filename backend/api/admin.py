from django.contrib import admin

from .reports import build_dashboard_report
from .models import (
    Announcement,
    Attachment,
    AuditLog,
    DeliveryLog,
    Document,
    Institution,
    PrivacyRequest,
    Profile,
    PushDevice,
    Segment,
    VisualIdentity,
)


admin.site.site_header = 'Administracao do Projeto Miranda'
admin.site.site_title = 'Projeto Miranda'
admin.site.index_title = 'Painel de administracao'
admin.site.index_template = 'admin/dashboard_index.html'

admin_site_index = admin.site.index


def dashboard_index(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context['dashboard_report'] = build_dashboard_report()
    return admin_site_index(request, extra_context=extra_context)


admin.site.index = dashboard_index


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone_number')


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'is_active', 'updated_at')
    list_filter = ('kind', 'is_active')
    search_fields = ('name', 'official_email')


@admin.register(VisualIdentity)
class VisualIdentityAdmin(admin.ModelAdmin):
    list_display = ('institution', 'primary_color', 'secondary_color', 'updated_at')
    search_fields = ('institution__name',)


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    filter_horizontal = ('users', 'push_devices')


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'pinned', 'institution', 'author', 'published_at')
    list_filter = ('status', 'pinned', 'institution')
    search_fields = ('title', 'content')
    filter_horizontal = ('segments',)
    inlines = [AttachmentInline]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'announcement', 'file_type', 'uploaded_at')
    list_filter = ('file_type',)
    search_fields = ('original_name', 'announcement__title')


@admin.register(PushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
    list_display = ('platform', 'user', 'is_active', 'updated_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('token', 'user__username', 'user__email')


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'recipient_user', 'channel', 'status', 'sent_at', 'viewed_at')
    list_filter = ('channel', 'status')
    search_fields = ('announcement__title', 'recipient_user__username', 'error_message')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'actor_username', 'action', 'target_type', 'target_id')
    list_filter = ('action', 'target_type', 'created_at')
    search_fields = ('actor_username', 'action', 'target_repr', 'target_id')
    readonly_fields = (
        'actor',
        'actor_username',
        'action',
        'target_type',
        'target_id',
        'target_repr',
        'metadata',
        'created_at',
    )


@admin.register(PrivacyRequest)
class PrivacyRequestAdmin(admin.ModelAdmin):
    list_display = ('request_type', 'status', 'requester_email', 'user', 'created_at', 'resolved_at')
    list_filter = ('request_type', 'status', 'created_at')
    search_fields = ('requester_name', 'requester_email', 'user__username', 'notes')
    readonly_fields = ('created_at', 'resolved_at', 'resolved_by')
