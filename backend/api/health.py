import os

from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .backup import build_backup_operational_status
from .media_validation import get_ffmpeg_executable
from .services import PushNotificationService


def timestamp():
    return timezone.now().isoformat()


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses=inline_serializer(
            name='HealthCheckResponse',
            fields={
                'status': serializers.CharField(),
                'timestamp': serializers.CharField(),
            },
        )
    )
    def get(self, request):
        return Response(
            {
                'status': 'healthy',
                'timestamp': timestamp(),
            }
        )


class DetailedHealthCheckView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        responses=inline_serializer(
            name='DetailedHealthCheckResponse',
            fields={
                'status': serializers.CharField(),
                'timestamp': serializers.CharField(),
                'environment': serializers.CharField(),
                'version': serializers.CharField(),
                'components': serializers.DictField(),
            },
        )
    )
    def get(self, request):
        components = {
            'database': check_database(),
            'cache': check_cache(),
            'firebase': check_firebase(),
            'cloudinary': check_cloudinary(),
            'video_processing': check_video_processing(),
            'backup_policy': build_backup_operational_status(),
        }
        overall_status = summarize_status(components)
        response_status = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if overall_status == 'unhealthy'
            else status.HTTP_200_OK
        )

        return Response(
            {
                'status': overall_status,
                'timestamp': timestamp(),
                'environment': 'development' if settings.DEBUG else 'production',
                'version': settings.SPECTACULAR_SETTINGS.get('VERSION', '1.0.0'),
                'components': components,
            },
            status=response_status,
        )


def check_database():
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return {'status': 'healthy'}
    except Exception as error:
        return {'status': 'unhealthy', 'detail': str(error)}


def check_cache():
    key = 'health-check'
    value = timezone.now().isoformat()
    try:
        cache.set(key, value, timeout=30)
        if cache.get(key) != value:
            return {'status': 'degraded', 'detail': 'Falha de escrita/leitura no cache.'}
        return {'status': 'healthy'}
    except Exception as error:
        return {'status': 'degraded', 'detail': str(error)}


def check_firebase():
    service = PushNotificationService()
    if service.is_configured:
        return {'status': 'healthy'}
    return {
        'status': 'degraded',
        'detail': 'Firebase push está desativado ou com credenciais incompletas.',
    }


def check_cloudinary():
    missing = [
        name
        for name in [
            'CLOUDINARY_CLOUD_NAME',
            'CLOUDINARY_API_KEY',
            'CLOUDINARY_API_SECRET',
        ]
        if not os.getenv(name)
    ]
    if missing:
        return {
            'status': 'degraded',
            'detail': f'Configuração ausente: {", ".join(missing)}.',
        }
    return {'status': 'healthy'}


def check_video_processing():
    if not getattr(settings, 'VIDEO_COMPRESSION_ENABLED', True):
        return {
            'status': 'degraded',
            'detail': 'Compressão automática de vídeo está desativada.',
        }

    ffmpeg_path = get_ffmpeg_executable()
    if not ffmpeg_path:
        return {
            'status': 'unhealthy',
            'detail': 'Executável do FFmpeg não foi encontrado.',
        }

    return {'status': 'healthy'}


def summarize_status(components):
    statuses = {component['status'] for component in components.values()}
    if 'unhealthy' in statuses:
        return 'unhealthy'
    if 'degraded' in statuses:
        return 'degraded'
    return 'healthy'
