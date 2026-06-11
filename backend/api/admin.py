from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .audit import record_audit_log
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


class AuditedAdminMixin:
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = 'updated' if change else 'created'
        record_audit_log(
            request.user,
            f'admin_{obj._meta.model_name}_{action}',
            obj,
        )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        deleted_objects = list(formset.deleted_objects)

        for obj in instances:
            action = 'updated' if obj.pk else 'created'
            obj.save()
            record_audit_log(
                request.user,
                f'admin_{obj._meta.model_name}_{action}',
                obj,
                {'parent': str(form.instance)},
            )

        formset.save_m2m()
        for obj in deleted_objects:
            record_audit_log(
                request.user,
                f'admin_{obj._meta.model_name}_delete_blocked',
                obj,
                {'parent': str(form.instance)},
            )


class NoDeleteAdminMixin:
    def has_delete_permission(self, request, obj=None):
        return False


class NoDeleteInlineMixin:
    def has_delete_permission(self, request, obj=None):
        return False


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


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(AuditedAdminMixin, NoDeleteAdminMixin, DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    actions = ('deactivate_selected_users',)

    @admin.action(description='Inativar usuarios selecionados e revogar acessos')
    def deactivate_selected_users(self, request, queryset):
        target_users = list(queryset.exclude(pk=request.user.pk))
        skipped_current_user = queryset.filter(pk=request.user.pk).exists()

        if not target_users:
            self.message_user(
                request,
                'Nenhum usuario foi inativado. A propria conta logada nao pode ser inativada por esta acao.',
                level=messages.WARNING,
            )
            return

        target_ids = [user.pk for user in target_users]
        users_updated = User.objects.filter(pk__in=target_ids).update(
            is_active=False,
            is_staff=False,
            is_superuser=False,
        )
        tokens_deleted, _ = Token.objects.filter(user_id__in=target_ids).delete()
        devices_updated = PushDevice.objects.filter(
            user_id__in=target_ids,
            is_active=True,
        ).update(is_active=False)

        for user in target_users:
            user.is_active = False
            user.is_staff = False
            user.is_superuser = False
            record_audit_log(
                request.user,
                'admin_user_deactivated',
                user,
                {
                    'tokens_deleted_total': tokens_deleted,
                    'push_devices_deactivated_total': devices_updated,
                },
            )

        message = (
            f'{users_updated} usuario(s) inativado(s), '
            f'{tokens_deleted} token(s) revogado(s) e '
            f'{devices_updated} dispositivo(s) push desativado(s).'
        )
        if skipped_current_user:
            message += ' A propria conta logada foi ignorada por seguranca.'

        self.message_user(request, message, level=messages.SUCCESS)


@admin.register(Document)
class DocumentAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(Profile)
class ProfileAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone_number')


@admin.register(Institution)
class InstitutionAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'kind', 'is_active', 'updated_at')
    list_filter = ('kind', 'is_active')
    search_fields = ('name', 'official_email')


@admin.register(VisualIdentity)
class VisualIdentityAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('institution', 'primary_color', 'secondary_color', 'updated_at')
    search_fields = ('institution__name',)


@admin.register(Segment)
class SegmentAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    filter_horizontal = ('users', 'push_devices')


class AttachmentInline(NoDeleteInlineMixin, admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(Announcement)
class AnnouncementAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'status', 'pinned', 'institution', 'author', 'published_at')
    list_filter = ('status', 'pinned', 'institution')
    search_fields = ('title', 'content')
    filter_horizontal = ('segments',)
    inlines = [AttachmentInline]


@admin.register(Attachment)
class AttachmentAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('original_name', 'announcement', 'file_type', 'uploaded_at')
    list_filter = ('file_type',)
    search_fields = ('original_name', 'announcement__title')


@admin.register(PushDevice)
class PushDeviceAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('platform', 'user', 'is_active', 'updated_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('token', 'user__username', 'user__email')


@admin.register(DeliveryLog)
class DeliveryLogAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('announcement', 'recipient_user', 'channel', 'status', 'sent_at', 'viewed_at')
    list_filter = ('channel', 'status')
    search_fields = ('announcement__title', 'recipient_user__username', 'error_message')


@admin.register(AuditLog)
class AuditLogAdmin(NoDeleteAdminMixin, admin.ModelAdmin):
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

    def has_add_permission(self, request):
        return False


@admin.register(PrivacyRequest)
class PrivacyRequestAdmin(AuditedAdminMixin, NoDeleteAdminMixin, admin.ModelAdmin):
    list_display = ('request_type', 'status', 'requester_email', 'user', 'created_at', 'resolved_at')
    list_filter = ('request_type', 'status', 'created_at')
    search_fields = ('requester_name', 'requester_email', 'user__username', 'notes')
    readonly_fields = ('created_at', 'resolved_at', 'resolved_by')
