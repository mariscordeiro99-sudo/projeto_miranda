from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .chat_views import (
    ChatContactsView,
    ChatMarkReadView,
    ChatMessagesView,
    ChatSendView,
    ChatUploadView,
)
from .views import (
    AnnouncementViewSet,
    AttachmentViewSet,
    AuditLogViewSet,
    DashboardMetricsView,
    DashboardReportView,
    DeactivateOwnAccountView,
    DeliveryLogViewSet,
    DocumentViewSet,
    HelloView,
    InstitutionViewSet,
    ManagerViewSet,
    PrivacyRequestViewSet,
    ProfileViewSet,
    PushDeviceViewSet,
    SegmentViewSet,
    VisualIdentityViewSet,
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'institutions', InstitutionViewSet, basename='institution')
router.register(r'segments', SegmentViewSet, basename='segment')
router.register(r'visual-identities', VisualIdentityViewSet, basename='visual-identity')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'push-devices', PushDeviceViewSet, basename='push-device')
router.register(r'delivery-logs', DeliveryLogViewSet, basename='delivery-log')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'privacy-requests', PrivacyRequestViewSet, basename='privacy-request')

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('chat/contatos', ChatContactsView.as_view(), name='chat-contacts'),
    path('chat/contatos/', ChatContactsView.as_view(), name='chat-contacts-slash'),
    path('chat/contatos/<int:contact_id>/ler', ChatMarkReadView.as_view(), name='chat-mark-read'),
    path('chat/contatos/<int:contact_id>/ler/', ChatMarkReadView.as_view(), name='chat-mark-read-slash'),
    path('chat/mensagens/<int:contact_id>', ChatMessagesView.as_view(), name='chat-messages'),
    path('chat/mensagens/<int:contact_id>/', ChatMessagesView.as_view(), name='chat-messages-slash'),
    path('chat/enviar', ChatSendView.as_view(), name='chat-send'),
    path('chat/enviar/', ChatSendView.as_view(), name='chat-send-slash'),
    path('chat/upload', ChatUploadView.as_view(), name='chat-upload'),
    path('chat/upload/', ChatUploadView.as_view(), name='chat-upload-slash'),
    path('reports/dashboard/', DashboardReportView.as_view(), name='dashboard-report'),
    path('privacy/deactivate-account/', DeactivateOwnAccountView.as_view(), name='privacy-deactivate-account'),
    path('', include(router.urls)),
]
