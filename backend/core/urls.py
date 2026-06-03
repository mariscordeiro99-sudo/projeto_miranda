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
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api import admin_report_views
from api.views import HelloView

urlpatterns = [
    path('', lambda request: redirect('admin/')), 
    path('admin/reports/users-active/', admin_report_views.active_users_report, name='admin-report-users-active'),
    path('admin/reports/announcements-published/', admin_report_views.published_announcements_report, name='admin-report-announcements-published'),
    path('admin/reports/devices-active/', admin_report_views.active_devices_report, name='admin-report-devices-active'),
    path('admin/reports/delivery-failures/', admin_report_views.failed_deliveries_report, name='admin-report-delivery-failures'),
    path('admin/', admin.site.urls),
    path('auth/', include('api.auth_urls')),
    path('health/', HelloView.as_view(), name='health'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
