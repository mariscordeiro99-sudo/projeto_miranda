from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnnouncementViewSet,
    AttachmentViewSet,
    DeliveryLogViewSet,
    DocumentViewSet,
    HelloView,
    InstitutionViewSet,
    ProfileViewSet,
    PushDeviceViewSet,
    VisualIdentityViewSet,
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'institutions', InstitutionViewSet, basename='institution')
router.register(r'visual-identities', VisualIdentityViewSet, basename='visual-identity')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'push-devices', PushDeviceViewSet, basename='push-device')
router.register(r'delivery-logs', DeliveryLogViewSet, basename='delivery-log')

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),
    path('', include(router.urls)),
]
