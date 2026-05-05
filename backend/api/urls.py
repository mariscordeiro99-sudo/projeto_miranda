from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HelloView, DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),
    path('', include(router.urls)),
]
