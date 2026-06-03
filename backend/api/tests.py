import struct
import tempfile
from shutil import rmtree

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APITestCase

from .models import Announcement, Attachment, DeliveryLog, Profile, PushDevice
from .views import validate_attachment


def mp4_atom(atom_type, payload):
    return struct.pack('>I', len(payload) + 8) + atom_type + payload


def mp4_file_with_duration(seconds):
    timescale = 1000
    duration = int(seconds * timescale)
    mvhd_payload = (
        b'\x00\x00\x00\x00'
        + struct.pack('>IIII', 0, 0, timescale, duration)
        + b'\x00' * 80
    )
    return (
        mp4_atom(b'ftyp', b'isom\x00\x00\x00\x01isom')
        + mp4_atom(b'moov', mp4_atom(b'mvhd', mvhd_payload))
    )


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()

    def tearDown(self):
        rmtree(self.media_root, ignore_errors=True)

    def test_public_register_cannot_create_manager(self):
        response = self.client.post(
            '/auth/register/',
            {
                'username': 'gestor_publico',
                'email': 'gestor@example.com',
                'password': 'SenhaForte123',
                'first_name': 'Gestor Publico',
                'phone_number': '51999999999',
                'is_gestor': 'true',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username='gestor_publico').exists())

    def test_public_register_creates_citizen(self):
        response = self.client.post(
            '/auth/register/',
            {
                'username': 'cidadao',
                'email': 'cidadao@example.com',
                'password': 'SenhaForte123',
                'first_name': 'Cidadao',
                'phone_number': '51988888888',
                'is_gestor': 'false',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='cidadao')
        self.assertFalse(user.is_staff)
        self.assertEqual(user.profile.role, Profile.ROLE_CITIZEN)

    def test_public_register_rejects_weak_password(self):
        response = self.client.post(
            '/auth/register/',
            {
                'username': 'senha_fraca',
                'email': 'senha_fraca@example.com',
                'password': '123',
                'first_name': 'Senha Fraca',
                'phone_number': '51966666666',
                'is_gestor': 'false',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='senha_fraca').exists())

    def test_public_register_accepts_profile_picture(self):
        test_storages = {
            'default': {
                'BACKEND': 'django.core.files.storage.FileSystemStorage',
            },
            'staticfiles': {
                'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
            },
        }

        with override_settings(MEDIA_ROOT=self.media_root, STORAGES=test_storages):
            response = self.client.post(
                '/auth/register/',
                {
                    'username': 'cidadao_foto',
                    'email': 'cidadao_foto@example.com',
                    'password': 'SenhaForte123',
                    'first_name': 'Cidadao Foto',
                    'phone_number': '51977777777',
                    'is_gestor': 'false',
                    'profile_picture': SimpleUploadedFile(
                        'perfil.png',
                        (
                            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
                            b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
                            b'\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT'
                            b'x\x9cc\xf8\xcfP\x0f\x00\x03\x86\x01\x80Z4}k'
                            b'\x00\x00\x00\x00IEND\xaeB`\x82'
                        ),
                        content_type='image/png',
                    ),
                },
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        profile = User.objects.get(username='cidadao_foto').profile
        self.assertTrue(profile.profile_picture.name)


class AttachmentValidationTests(APITestCase):
    def test_video_with_60_seconds_is_allowed(self):
        uploaded_file = SimpleUploadedFile(
            'video.mp4',
            mp4_file_with_duration(60),
            content_type='video/mp4',
        )

        validate_attachment(uploaded_file)

    def test_video_over_60_seconds_is_blocked(self):
        uploaded_file = SimpleUploadedFile(
            'video.mp4',
            mp4_file_with_duration(61),
            content_type='video/mp4',
        )

        with self.assertRaises(DRFValidationError):
            validate_attachment(uploaded_file)


class PublicDataExposureTests(APITestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.test_storages = {
            'default': {
                'BACKEND': 'django.core.files.storage.FileSystemStorage',
            },
            'staticfiles': {
                'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
            },
        }
        self.staff_user = User.objects.create_user(
            username='gestor',
            email='gestor@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        self.published = Announcement.objects.create(
            author=self.staff_user,
            title='Publicado',
            content='Conteudo publicado',
            status=Announcement.STATUS_PUBLISHED,
        )
        self.draft = Announcement.objects.create(
            author=self.staff_user,
            title='Rascunho',
            content='Conteudo privado',
            status=Announcement.STATUS_DRAFT,
        )

    def tearDown(self):
        rmtree(self.media_root, ignore_errors=True)

    def create_attachment(self, announcement, name):
        return Attachment.objects.create(
            announcement=announcement,
            file=SimpleUploadedFile(name, b'%PDF-1.4\n', content_type='application/pdf'),
            original_name=name,
            file_type=Attachment.TYPE_DOCUMENT,
        )

    def test_public_attachment_list_only_includes_published_announcements(self):
        with override_settings(MEDIA_ROOT=self.media_root, STORAGES=self.test_storages):
            published_attachment = self.create_attachment(self.published, 'publico.pdf')
            draft_attachment = self.create_attachment(self.draft, 'rascunho.pdf')

            response = self.client.get('/api/attachments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data}
        self.assertIn(published_attachment.id, returned_ids)
        self.assertNotIn(draft_attachment.id, returned_ids)

    def test_staff_attachment_list_includes_draft_announcements(self):
        token = Token.objects.create(user=self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

        with override_settings(MEDIA_ROOT=self.media_root, STORAGES=self.test_storages):
            draft_attachment = self.create_attachment(self.draft, 'rascunho.pdf')

            response = self.client.get('/api/attachments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data}
        self.assertIn(draft_attachment.id, returned_ids)

    def test_public_announcement_does_not_expose_author_email_or_staff_flag(self):
        response = self.client.get(f'/api/announcements/{self.published.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('author', response.data)
        self.assertNotIn('email', response.data['author'])
        self.assertNotIn('is_staff', response.data['author'])


class DashboardReportTests(APITestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        Profile.objects.create(
            user=self.staff_user,
            phone_number='51911111111',
            role=Profile.ROLE_MANAGER,
        )

        self.citizen_user = User.objects.create_user(
            username='cidadao_relatorio',
            email='cidadao_relatorio@example.com',
            password='SenhaForte123',
        )
        Profile.objects.create(
            user=self.citizen_user,
            phone_number='51922222222',
            role=Profile.ROLE_CITIZEN,
        )

        self.inactive_user = User.objects.create_user(
            username='inativo',
            email='inativo@example.com',
            password='SenhaForte123',
            is_active=False,
        )

        self.published = Announcement.objects.create(
            author=self.staff_user,
            title='Comunicado publicado',
            content='Conteudo publicado',
            status=Announcement.STATUS_PUBLISHED,
            pinned=True,
        )
        self.draft = Announcement.objects.create(
            author=self.staff_user,
            title='Comunicado rascunho',
            content='Conteudo rascunho',
            status=Announcement.STATUS_DRAFT,
        )
        Announcement.objects.create(
            author=self.staff_user,
            title='Comunicado arquivado',
            content='Conteudo arquivado',
            status=Announcement.STATUS_ARCHIVED,
        )

        self.active_device = PushDevice.objects.create(
            user=self.citizen_user,
            token='active-web-token',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.inactive_device = PushDevice.objects.create(
            token='inactive-android-token',
            platform=PushDevice.PLATFORM_ANDROID,
            is_active=False,
        )

        DeliveryLog.objects.create(
            announcement=self.published,
            device=self.active_device,
            recipient_user=self.citizen_user,
            status=DeliveryLog.STATUS_VIEWED,
            viewed_at=timezone.now(),
        )
        DeliveryLog.objects.create(
            announcement=self.published,
            device=self.active_device,
            recipient_user=self.citizen_user,
            status=DeliveryLog.STATUS_SENT,
        )
        DeliveryLog.objects.create(
            announcement=self.published,
            device=self.inactive_device,
            status=DeliveryLog.STATUS_FAILED,
            error_message='Provider returned invalid token while sending notification.',
        )
        DeliveryLog.objects.create(
            announcement=self.draft,
            device=self.active_device,
            recipient_user=self.citizen_user,
            status=DeliveryLog.STATUS_PENDING,
        )

    def authenticate_as(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    def test_dashboard_requires_authenticated_admin(self):
        response = self.client.get('/api/reports/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_rejects_non_admin_user(self):
        self.authenticate_as(self.citizen_user)

        response = self.client.get('/api/reports/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_returns_general_metrics_for_admin(self):
        self.authenticate_as(self.staff_user)

        response = self.client.get('/api/reports/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['users']['total'], 3)
        self.assertEqual(response.data['users']['active'], 2)
        self.assertEqual(response.data['users']['staff'], 1)
        self.assertEqual(response.data['users']['citizens'], 1)
        self.assertEqual(response.data['users']['managers'], 1)
        self.assertEqual(response.data['users']['with_active_push_device'], 1)

        self.assertEqual(response.data['announcements']['total'], 3)
        self.assertEqual(response.data['announcements']['published'], 1)
        self.assertEqual(response.data['announcements']['draft'], 1)
        self.assertEqual(response.data['announcements']['archived'], 1)
        self.assertEqual(response.data['announcements']['pinned'], 1)

        self.assertEqual(response.data['delivery']['total_logs'], 4)
        self.assertEqual(response.data['delivery']['pending'], 1)
        self.assertEqual(response.data['delivery']['sent'], 2)
        self.assertEqual(response.data['delivery']['failed'], 1)
        self.assertEqual(response.data['delivery']['viewed'], 1)
        self.assertEqual(response.data['delivery']['view_rate'], 25.0)
        self.assertEqual(response.data['delivery']['failure_rate'], 25.0)

        self.assertEqual(response.data['devices']['total'], 2)
        self.assertEqual(response.data['devices']['active'], 1)
        self.assertEqual(response.data['devices']['inactive'], 1)
        self.assertEqual(response.data['devices']['anonymous'], 1)
        self.assertEqual(response.data['devices']['by_platform'][PushDevice.PLATFORM_WEB], 1)
        self.assertEqual(response.data['devices']['by_platform'][PushDevice.PLATFORM_ANDROID], 1)
        self.assertEqual(response.data['devices']['by_platform'][PushDevice.PLATFORM_IOS], 0)
        self.assertLessEqual(len(response.data['recent_announcements']), 5)

        self.assertEqual(len(response.data['active_devices']), 1)
        self.assertEqual(response.data['active_devices'][0]['platform'], PushDevice.PLATFORM_WEB)
        self.assertEqual(response.data['active_devices'][0]['user'], 'cidadao_relatorio')
        self.assertTrue(response.data['active_devices'][0]['token_preview'].endswith('...'))
        self.assertNotEqual(
            response.data['active_devices'][0]['token_preview'],
            self.active_device.token,
        )

        self.assertEqual(len(response.data['recent_failures']), 1)
        self.assertEqual(
            response.data['recent_failures'][0]['announcement'],
            self.published.title,
        )
        self.assertIn('invalid token', response.data['recent_failures'][0]['error_message'])

        self.assertEqual(len(response.data['recent_views']), 1)
        self.assertEqual(response.data['recent_views'][0]['recipient'], 'cidadao_relatorio')
        self.assertEqual(response.data['recent_views'][0]['announcement'], self.published.title)


@override_settings(
    STORAGES={
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
)
class AdminDashboardTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin_dashboard',
            email='admin_dashboard@example.com',
            password='SenhaForte123',
        )
        self.citizen_user = User.objects.create_user(
            username='admin_report_citizen',
            email='admin_report_citizen@example.com',
            password='SenhaForte123',
        )
        self.announcement = Announcement.objects.create(
            author=self.admin_user,
            title='Relatorio publicado',
            content='Conteudo publicado',
            status=Announcement.STATUS_PUBLISHED,
        )
        self.device = PushDevice.objects.create(
            user=self.citizen_user,
            token='admin-report-device-token',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.failed_log = DeliveryLog.objects.create(
            announcement=self.announcement,
            device=self.device,
            recipient_user=self.citizen_user,
            status=DeliveryLog.STATUS_FAILED,
            error_message='Falha de envio para teste',
        )

    def test_admin_index_shows_dashboard_report(self):
        self.client.force_login(self.admin_user)

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Relatorios gerais')
        self.assertContains(response, 'usuarios ativos')
        self.assertContains(response, 'comunicados publicados')
        self.assertContains(response, 'dispositivos ativos')
        self.assertContains(response, 'falhas de envio')
        self.assertContains(response, 'Ações recentes')
        self.assertContains(response, 'entregas enviadas')
        self.assertContains(response, 'taxa de visualizacao')

    def test_admin_report_detail_pages_are_custom_and_staff_only(self):
        urls = [
            ('/admin/reports/users-active/', 'Usuarios ativos'),
            ('/admin/reports/announcements-published/', 'Comunicados publicados'),
            ('/admin/reports/devices-active/', 'Dispositivos ativos'),
            ('/admin/reports/delivery-failures/', 'Falhas de envio'),
        ]

        for url, _ in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.client.force_login(self.admin_user)

        for url, title in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertContains(response, title)
            self.assertContains(response, 'Voltar para relatorios')
