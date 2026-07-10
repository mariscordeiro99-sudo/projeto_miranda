"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api import admin_report_views
from api.chat_views import (
    ChatContactsView,
    ChatMarkReadView,
    ChatMessagesView,
    ChatSendView,
    ChatUploadView,
)
from api.health import DetailedHealthCheckView, HealthCheckView
from api.views import AdminAnnouncementsView, DashboardMetricsView, FrontendAnnouncementsView, FrontendVisualIdentityView, UserPermissionsView

urlpatterns = [
    path('', lambda request: redirect('admin/')), 
    path('admin/reports/users-active/', admin_report_views.active_users_report, name='admin-report-users-active'),
    path('admin/reports/announcements-published/', admin_report_views.published_announcements_report, name='admin-report-announcements-published'),
    path('admin/reports/devices-active/', admin_report_views.active_devices_report, name='admin-report-devices-active'),
    path('admin/reports/delivery-failures/', admin_report_views.failed_deliveries_report, name='admin-report-delivery-failures'),
    path('admin/users-permissions/', UserPermissionsView.as_view(), name='user-permissions-list'),
    path('admin/users-permissions/<int:user_id>/', UserPermissionsView.as_view(), name='user-permissions-detail'),
    path('admin/announcements/', AdminAnnouncementsView.as_view(), name='admin-announcements-list'),
    path('admin/announcements', AdminAnnouncementsView.as_view(), name='admin-announcements-list-noslash'),
    path('admin/announcements/<int:announcement_id>/', AdminAnnouncementsView.as_view(), name='admin-announcements-detail'),
    path('admin/announcements/<int:announcement_id>', AdminAnnouncementsView.as_view(), name='admin-announcements-detail-noslash'),
    path('admin/', admin.site.urls),
    path('auth/', include('api.auth_urls')),
    path('announcements/', FrontendAnnouncementsView.as_view(), name='frontend-announcements-root-slash'),
    path('announcements', FrontendAnnouncementsView.as_view(), name='frontend-announcements-root'),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics-root'),
    path('instituicao/identidade-visual', FrontendVisualIdentityView.as_view(), name='frontend-visual-identity-root'),
    path('instituicao/identidade-visual/', FrontendVisualIdentityView.as_view(), name='frontend-visual-identity-root-slash'),
    path('instituicao/identidade-visual/atualizar', FrontendVisualIdentityView.as_view(), name='frontend-visual-identity-update-root'),
    path('instituicao/identidade-visual/atualizar/', FrontendVisualIdentityView.as_view(), name='frontend-visual-identity-update-root-slash'),
    path('chat/contatos', ChatContactsView.as_view(), name='chat-contacts-root'),
    path('chat/contatos/', ChatContactsView.as_view(), name='chat-contacts-root-slash'),
    path('chat/contatos/<int:contact_id>/ler', ChatMarkReadView.as_view(), name='chat-mark-read-root'),
    path('chat/contatos/<int:contact_id>/ler/', ChatMarkReadView.as_view(), name='chat-mark-read-root-slash'),
    path('chat/mensagens/<int:contact_id>', ChatMessagesView.as_view(), name='chat-messages-root'),
    path('chat/mensagens/<int:contact_id>/', ChatMessagesView.as_view(), name='chat-messages-root-slash'),
    path('chat/enviar', ChatSendView.as_view(), name='chat-send-root'),
    path('chat/enviar/', ChatSendView.as_view(), name='chat-send-root-slash'),
    path('chat/upload', ChatUploadView.as_view(), name='chat-upload-root'),
    path('chat/upload/', ChatUploadView.as_view(), name='chat-upload-root-slash'),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('health/detailed/', DetailedHealthCheckView.as_view(), name='health-detailed'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^api/(?P<version>v[0-9]+)/', include('api.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
