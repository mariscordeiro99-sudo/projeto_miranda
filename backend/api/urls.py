from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnnouncementViewSet,
    AttachmentViewSet,
    AuditLogViewSet,
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
    path('reports/dashboard/', DashboardReportView.as_view(), name='dashboard-report'),
    path('privacy/deactivate-account/', DeactivateOwnAccountView.as_view(), name='privacy-deactivate-account'),
    path('', include(router.urls)),
]
