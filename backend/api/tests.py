import struct
import tempfile
from datetime import timedelta
from shutil import rmtree
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APITestCase

from .models import (
    Announcement,
    Attachment,
    AuditLog,
    DeliveryLog,
    Institution,
    PrivacyRequest,
    Profile,
    PushDevice,
    Segment,
)
from .media_validation import validate_attachment


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


class SizedUpload:
    def __init__(self, size, content_type):
        self.size = size
        self.content_type = content_type


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


class ManagerTokenPolicyTests(APITestCase):
    def setUp(self):
        self.manager_user = User.objects.create_user(
            username='gestor_token',
            email='gestor_token@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        Profile.objects.create(
            user=self.manager_user,
            phone_number='51911111111',
            role=Profile.ROLE_MANAGER,
        )
        self.citizen_user = User.objects.create_user(
            username='cidadao_token',
            email='cidadao_token@example.com',
            password='SenhaForte123',
        )
        Profile.objects.create(
            user=self.citizen_user,
            phone_number='51922222222',
            role=Profile.ROLE_CITIZEN,
        )

    @override_settings(MANAGER_TOKEN_ROTATE_ON_LOGIN=True, MANAGER_TOKEN_TTL_SECONDS=3600)
    def test_manager_login_rotates_existing_token_and_returns_expiration(self):
        old_token = Token.objects.create(user=self.manager_user)

        response = self.client.post(
            '/auth/login/',
            {
                'username': self.manager_user.username,
                'password': 'SenhaForte123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['expires_in'], 3600)
        self.assertNotEqual(response.data['token'], old_token.key)
        self.assertFalse(Token.objects.filter(key=old_token.key).exists())
        self.assertTrue(Token.objects.filter(key=response.data['token']).exists())

    @override_settings(MANAGER_TOKEN_TTL_SECONDS=60)
    def test_expired_manager_token_is_rejected_and_revoked(self):
        token = Token.objects.create(user=self.manager_user)
        Token.objects.filter(key=token.key).update(
            created=timezone.now() - timedelta(seconds=61)
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

        response = self.client.get('/api/reports/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Token.objects.filter(key=token.key).exists())

    @override_settings(MANAGER_TOKEN_TTL_SECONDS=60)
    def test_citizen_token_is_not_expired_by_manager_policy(self):
        token = Token.objects.create(user=self.citizen_user)
        Token.objects.filter(key=token.key).update(
            created=timezone.now() - timedelta(days=30)
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

        response = self.client.get('/api/profiles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Token.objects.filter(key=token.key).exists())

    def test_password_reset_revokes_existing_tokens(self):
        token = Token.objects.create(user=self.citizen_user)
        uid = urlsafe_base64_encode(force_bytes(self.citizen_user.pk))
        reset_token = default_token_generator.make_token(self.citizen_user)

        response = self.client.post(
            '/auth/password-reset-confirm/',
            {
                'uid': uid,
                'token': reset_token,
                'new_password': 'NovaSenhaForte123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(key=token.key).exists())


class ManagerManagementTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_gestores',
            email='admin_gestores@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        Profile.objects.create(
            user=self.admin_user,
            phone_number='51911111111',
            role=Profile.ROLE_MANAGER,
        )
        self.citizen_user = User.objects.create_user(
            username='cidadao_gestores',
            email='cidadao_gestores@example.com',
            password='SenhaForte123',
        )
        Profile.objects.create(
            user=self.citizen_user,
            phone_number='51922222222',
            role=Profile.ROLE_CITIZEN,
        )

    def authenticate_as(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        return token

    def create_manager(self, username='gestor_criado'):
        manager = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='SenhaForte123',
            first_name='Gestor Criado',
            is_staff=True,
        )
        Profile.objects.create(
            user=manager,
            phone_number='51933333333',
            role=Profile.ROLE_MANAGER,
        )
        return manager

    def test_managers_endpoint_requires_admin_user(self):
        anonymous_response = self.client.get('/api/managers/')
        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_as(self.citizen_user)
        citizen_response = self.client.get('/api/managers/')
        self.assertEqual(citizen_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_manager(self):
        self.authenticate_as(self.admin_user)

        response = self.client.post(
            '/api/managers/',
            {
                'username': 'novo_gestor',
                'email': 'novo_gestor@example.com',
                'password': 'SenhaForte123',
                'first_name': 'Novo Gestor',
                'phone_number': '51944444444',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        manager = User.objects.get(username='novo_gestor')
        self.assertTrue(manager.is_staff)
        self.assertTrue(manager.is_active)
        self.assertEqual(manager.profile.role, Profile.ROLE_MANAGER)
        self.assertEqual(manager.profile.phone_number, '51944444444')
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.admin_user,
                action='manager_created',
                target_id=str(manager.id),
            ).exists()
        )

    def test_admin_can_update_manager_contact_data(self):
        manager = self.create_manager()
        self.authenticate_as(self.admin_user)

        response = self.client.patch(
            f'/api/managers/{manager.id}/',
            {
                'first_name': 'Gestor Atualizado',
                'phone_number': '51955555555',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        manager.refresh_from_db()
        manager.profile.refresh_from_db()
        self.assertEqual(manager.first_name, 'Gestor Atualizado')
        self.assertEqual(manager.profile.phone_number, '51955555555')
        self.assertTrue(manager.is_staff)
        self.assertEqual(manager.profile.role, Profile.ROLE_MANAGER)

    def test_admin_can_deactivate_and_reactivate_manager(self):
        manager = self.create_manager()
        self.authenticate_as(self.admin_user)

        deactivate_response = self.client.post(f'/api/managers/{manager.id}/deactivate/')
        self.assertEqual(deactivate_response.status_code, status.HTTP_200_OK)
        manager.refresh_from_db()
        self.assertFalse(manager.is_active)

        reactivate_response = self.client.post(f'/api/managers/{manager.id}/reactivate/')
        self.assertEqual(reactivate_response.status_code, status.HTTP_200_OK)
        manager.refresh_from_db()
        manager.profile.refresh_from_db()
        self.assertTrue(manager.is_active)
        self.assertTrue(manager.is_staff)
        self.assertEqual(manager.profile.role, Profile.ROLE_MANAGER)

    def test_admin_can_revoke_manager_access(self):
        manager = self.create_manager()
        manager_token = Token.objects.create(user=manager)
        self.authenticate_as(self.admin_user)

        response = self.client.post(f'/api/managers/{manager.id}/revoke/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        manager.refresh_from_db()
        manager.profile.refresh_from_db()
        self.assertFalse(manager.is_staff)
        self.assertTrue(manager.is_active)
        self.assertEqual(manager.profile.role, Profile.ROLE_CITIZEN)
        self.assertFalse(Token.objects.filter(key=manager_token.key).exists())

    def test_admin_cannot_deactivate_or_revoke_self(self):
        self.authenticate_as(self.admin_user)

        deactivate_response = self.client.post(f'/api/managers/{self.admin_user.id}/deactivate/')
        revoke_response = self.client.post(f'/api/managers/{self.admin_user.id}/revoke/')

        self.assertEqual(deactivate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(revoke_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin_user.refresh_from_db()
        self.admin_user.profile.refresh_from_db()
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_active)
        self.assertEqual(self.admin_user.profile.role, Profile.ROLE_MANAGER)


class PrivacyAndAuditTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_lgpd',
            email='admin_lgpd@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        Profile.objects.create(
            user=self.admin_user,
            phone_number='51911111111',
            role=Profile.ROLE_MANAGER,
        )
        self.citizen_user = User.objects.create_user(
            username='cidadao_lgpd',
            email='cidadao_lgpd@example.com',
            password='SenhaForte123',
        )
        Profile.objects.create(
            user=self.citizen_user,
            phone_number='51922222222',
            role=Profile.ROLE_CITIZEN,
        )

    def authenticate_as(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        return token

    def test_audit_logs_are_admin_only(self):
        AuditLog.objects.create(
            actor=self.admin_user,
            actor_username=self.admin_user.username,
            action='test_action',
        )

        anonymous_response = self.client.get('/api/audit-logs/')
        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_as(self.citizen_user)
        citizen_response = self.client.get('/api/audit-logs/')
        self.assertEqual(citizen_response.status_code, status.HTTP_403_FORBIDDEN)

        self.authenticate_as(self.admin_user)
        admin_response = self.client.get('/api/audit-logs/')
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data['results'][0]['action'], 'test_action')

    def test_citizen_can_create_and_list_own_privacy_request(self):
        self.authenticate_as(self.citizen_user)

        response = self.client.post(
            '/api/privacy-requests/',
            {
                'request_type': PrivacyRequest.TYPE_ERASURE,
                'notes': 'Quero solicitar exclusao dos meus dados.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        privacy_request = PrivacyRequest.objects.get(id=response.data['id'])
        self.assertEqual(privacy_request.user, self.citizen_user)
        self.assertEqual(privacy_request.requester_email, self.citizen_user.email)
        self.assertEqual(privacy_request.status, PrivacyRequest.STATUS_PENDING)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.citizen_user,
                action='privacy_request_created',
                target_id=str(privacy_request.id),
            ).exists()
        )

        list_response = self.client.get('/api/privacy-requests/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['results']), 1)

    def test_admin_can_complete_privacy_request(self):
        privacy_request = PrivacyRequest.objects.create(
            user=self.citizen_user,
            requester_name='Cidadao LGPD',
            requester_email=self.citizen_user.email,
            request_type=PrivacyRequest.TYPE_EXPORT,
        )
        self.authenticate_as(self.admin_user)

        response = self.client.post(
            f'/api/privacy-requests/{privacy_request.id}/complete/',
            {'notes': 'Dados exportados e enviados ao solicitante.'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        privacy_request.refresh_from_db()
        self.assertEqual(privacy_request.status, PrivacyRequest.STATUS_COMPLETED)
        self.assertEqual(privacy_request.resolved_by, self.admin_user)
        self.assertIsNotNone(privacy_request.resolved_at)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.admin_user,
                action='privacy_request_completed',
                target_id=str(privacy_request.id),
            ).exists()
        )

    def test_citizen_can_deactivate_own_account_and_token_is_revoked(self):
        token = self.authenticate_as(self.citizen_user)

        response = self.client.post('/api/privacy/deactivate-account/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.citizen_user.refresh_from_db()
        self.assertFalse(self.citizen_user.is_active)
        self.assertFalse(Token.objects.filter(key=token.key).exists())
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.citizen_user,
                action='account_deactivated_by_owner',
                target_id=str(self.citizen_user.id),
            ).exists()
        )

    def test_admin_cannot_deactivate_own_account_by_privacy_endpoint(self):
        self.authenticate_as(self.admin_user)

        response = self.client.post('/api/privacy/deactivate-account/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)


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

    def test_attachment_over_60mb_is_blocked(self):
        uploaded_file = SizedUpload(
            size=(60 * 1024 * 1024) + 1,
            content_type='application/pdf',
        )

        with self.assertRaises(DRFValidationError):
            validate_attachment(uploaded_file)

    def test_unsupported_attachment_type_is_blocked(self):
        uploaded_file = SimpleUploadedFile(
            'script.exe',
            b'MZ',
            content_type='application/x-msdownload',
        )

        with self.assertRaises(DRFValidationError):
            validate_attachment(uploaded_file)


class AttachmentUploadAPITests(APITestCase):
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
            username='gestor_upload',
            email='gestor_upload@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        Profile.objects.create(
            user=self.staff_user,
            phone_number='51911111111',
            role=Profile.ROLE_MANAGER,
        )

    def tearDown(self):
        rmtree(self.media_root, ignore_errors=True)

    def authenticate_as_staff(self):
        token = Token.objects.create(user=self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    def png_file(self, name='imagem.png'):
        return SimpleUploadedFile(
            name,
            (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
                b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
                b'\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT'
                b'x\x9cc\xf8\xcfP\x0f\x00\x03\x86\x01\x80Z4}k'
                b'\x00\x00\x00\x00IEND\xaeB`\x82'
            ),
            content_type='image/png',
        )

    def test_staff_can_upload_pdf_word_docx_and_image_with_announcement(self):
        self.authenticate_as_staff()

        with override_settings(MEDIA_ROOT=self.media_root, STORAGES=self.test_storages):
            response = self.client.post(
                '/api/announcements/',
                {
                    'title': 'Comunicado com anexos',
                    'content': 'Conteudo com arquivos oficiais.',
                    'status': Announcement.STATUS_DRAFT,
                    'attachments': [
                        SimpleUploadedFile(
                            'edital.pdf',
                            b'%PDF-1.4\n',
                            content_type='application/pdf',
                        ),
                        SimpleUploadedFile(
                            'oficio.doc',
                            b'DOC',
                            content_type='application/msword',
                        ),
                        SimpleUploadedFile(
                            'ata.docx',
                            b'DOCX',
                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        ),
                        self.png_file(),
                    ],
                },
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        announcement = Announcement.objects.get(id=response.data['id'])
        attachments = list(announcement.attachments.order_by('original_name'))
        self.assertEqual(len(attachments), 4)

        file_types = {attachment.original_name: attachment.file_type for attachment in attachments}
        self.assertEqual(file_types['ata.docx'], Attachment.TYPE_DOCUMENT)
        self.assertEqual(file_types['edital.pdf'], Attachment.TYPE_DOCUMENT)
        self.assertEqual(file_types['oficio.doc'], Attachment.TYPE_DOCUMENT)
        self.assertEqual(file_types['imagem.png'], Attachment.TYPE_IMAGE)

    def test_attachment_endpoint_classifies_single_image_upload(self):
        self.authenticate_as_staff()
        announcement = Announcement.objects.create(
            author=self.staff_user,
            title='Comunicado imagem',
            content='Conteudo',
            status=Announcement.STATUS_DRAFT,
        )

        with override_settings(MEDIA_ROOT=self.media_root, STORAGES=self.test_storages):
            response = self.client.post(
                '/api/attachments/',
                {
                    'announcement': announcement.id,
                    'file': self.png_file('foto.png'),
                },
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attachment = Attachment.objects.get(id=response.data['id'])
        self.assertEqual(attachment.original_name, 'foto.png')
        self.assertEqual(attachment.file_type, Attachment.TYPE_IMAGE)

    def test_invalid_attachment_upload_is_rejected_before_announcement_is_saved(self):
        self.authenticate_as_staff()

        with override_settings(MEDIA_ROOT=self.media_root, STORAGES=self.test_storages):
            response = self.client.post(
                '/api/announcements/',
                {
                    'title': 'Comunicado invalido',
                    'content': 'Nao deve persistir se anexo falhar.',
                    'status': Announcement.STATUS_DRAFT,
                    'attachments': [
                        SimpleUploadedFile(
                            'malware.exe',
                            b'MZ',
                            content_type='application/x-msdownload',
                        ),
                    ],
                },
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Announcement.objects.filter(title='Comunicado invalido').exists())
        self.assertFalse(Attachment.objects.filter(original_name='malware.exe').exists())


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
        returned_ids = {item['id'] for item in response.data['results']}
        self.assertIn(published_attachment.id, returned_ids)
        self.assertNotIn(draft_attachment.id, returned_ids)

    def test_staff_attachment_list_includes_draft_announcements(self):
        token = Token.objects.create(user=self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

        with override_settings(MEDIA_ROOT=self.media_root, STORAGES=self.test_storages):
            draft_attachment = self.create_attachment(self.draft, 'rascunho.pdf')

            response = self.client.get('/api/attachments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data['results']}
        self.assertIn(draft_attachment.id, returned_ids)

    def test_public_announcement_does_not_expose_author_email_or_staff_flag(self):
        response = self.client.get(f'/api/announcements/{self.published.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('author', response.data)
        self.assertNotIn('email', response.data['author'])
        self.assertNotIn('is_staff', response.data['author'])

    def test_announcement_list_supports_pagination_search_filter_and_ordering(self):
        Announcement.objects.create(
            author=self.staff_user,
            title='Publicado sobre saude',
            content='Conteudo pesquisavel',
            status=Announcement.STATUS_PUBLISHED,
        )

        response = self.client.get(
            '/api/announcements/?status=published&search=Publicado&page_size=1&ordering=title'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Publicado')

    def test_staff_can_filter_draft_announcements(self):
        token = Token.objects.create(user=self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

        response = self.client.get('/api/announcements/?status=draft')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['id'] for item in response.data['results']}
        self.assertIn(self.draft.id, returned_ids)
        self.assertNotIn(self.published.id, returned_ids)


class DestructiveDeleteProtectionTests(APITestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='gestor_delete',
            email='gestor_delete@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        self.citizen_user = User.objects.create_user(
            username='cidadao_delete',
            email='cidadao_delete@example.com',
            password='SenhaForte123',
        )
        self.device = PushDevice.objects.create(
            user=self.citizen_user,
            token='delete-protection-token',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.announcement = Announcement.objects.create(
            author=self.staff_user,
            title='Comunicado protegido',
            content='Historico oficial protegido',
            status=Announcement.STATUS_PUBLISHED,
        )
        self.attachment = Attachment.objects.create(
            announcement=self.announcement,
            file='announcements/protegido.pdf',
            original_name='protegido.pdf',
            file_type=Attachment.TYPE_DOCUMENT,
        )
        self.delivery_log = DeliveryLog.objects.create(
            announcement=self.announcement,
            device=self.device,
            recipient_user=self.citizen_user,
            status=DeliveryLog.STATUS_SENT,
        )

    def authenticate_as_staff(self):
        token = Token.objects.create(user=self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    def test_delete_is_blocked_for_official_records_and_logs(self):
        self.authenticate_as_staff()

        endpoints = [
            f'/api/announcements/{self.announcement.id}/',
            f'/api/attachments/{self.attachment.id}/',
            f'/api/delivery-logs/{self.delivery_log.id}/',
        ]

        for endpoint in endpoints:
            response = self.client.delete(endpoint)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.assertTrue(Announcement.objects.filter(id=self.announcement.id).exists())
        self.assertTrue(Attachment.objects.filter(id=self.attachment.id).exists())
        self.assertTrue(DeliveryLog.objects.filter(id=self.delivery_log.id).exists())


class HealthCheckTests(APITestCase):
    def test_simple_health_check_is_public(self):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('timestamp', response.data)

    def test_detailed_health_check_requires_admin(self):
        response = self.client.get('/health/detailed/')

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_detailed_health_check_returns_components_for_admin(self):
        admin_user = User.objects.create_user(
            username='admin_health',
            email='admin_health@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

        response = self.client.get('/health/detailed/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data['status'], ['healthy', 'degraded'])
        self.assertIn('database', response.data['components'])
        self.assertIn('cache', response.data['components'])


class ApiVersioningTests(APITestCase):
    def test_v1_api_prefix_keeps_existing_routes_available(self):
        response = self.client.get('/api/v1/hello/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')


class DeliveryViewTrackingTests(APITestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='gestor_visualizacao',
            email='gestor_visualizacao@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        self.citizen_user = User.objects.create_user(
            username='cidadao_visualizacao',
            email='cidadao_visualizacao@example.com',
            password='SenhaForte123',
        )
        self.device = PushDevice.objects.create(
            user=self.citizen_user,
            token='view-device-token',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.announcement = Announcement.objects.create(
            author=self.staff_user,
            title='Comunicado para visualizar',
            content='Conteudo do comunicado',
            status=Announcement.STATUS_DRAFT,
        )

    def authenticate_as(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    def test_publish_creates_only_one_delivery_log_per_device(self):
        self.authenticate_as(self.staff_user)

        first_response = self.client.post(f'/api/announcements/{self.announcement.id}/publish/')
        second_response = self.client.post(f'/api/announcements/{self.announcement.id}/publish/')

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            DeliveryLog.objects.filter(
                announcement=self.announcement,
                device=self.device,
            ).count(),
            1,
        )

    def test_authenticated_citizen_marks_own_announcement_as_viewed(self):
        self.announcement.status = Announcement.STATUS_PUBLISHED
        self.announcement.save()
        log = DeliveryLog.objects.create(
            announcement=self.announcement,
            device=self.device,
            recipient_user=self.citizen_user,
            status=DeliveryLog.STATUS_SENT,
        )
        self.authenticate_as(self.citizen_user)

        response = self.client.post(
            f'/api/announcements/{self.announcement.id}/mark-viewed/',
            {'delivery_log_id': log.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log.refresh_from_db()
        self.assertEqual(log.status, DeliveryLog.STATUS_VIEWED)
        self.assertIsNotNone(log.viewed_at)

        self.authenticate_as(self.staff_user)
        stats_response = self.client.get(f'/api/announcements/{self.announcement.id}/stats/')
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stats_response.data['viewed'], 1)
        self.assertEqual(stats_response.data['view_rate'], 100.0)

    def test_device_token_can_mark_anonymous_delivery_as_viewed(self):
        self.announcement.status = Announcement.STATUS_PUBLISHED
        self.announcement.save()
        anonymous_device = PushDevice.objects.create(
            token='anonymous-view-token',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        log = DeliveryLog.objects.create(
            announcement=self.announcement,
            device=anonymous_device,
            status=DeliveryLog.STATUS_SENT,
        )

        response = self.client.post(
            f'/api/announcements/{self.announcement.id}/mark-viewed/',
            {
                'delivery_log_id': log.id,
                'device_token': anonymous_device.token,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log.refresh_from_db()
        self.assertEqual(log.status, DeliveryLog.STATUS_VIEWED)


class AutomaticPushDispatchTests(APITestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='gestor_push',
            email='gestor_push@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        self.citizen_user = User.objects.create_user(
            username='cidadao_push',
            email='cidadao_push@example.com',
            password='SenhaForte123',
        )
        self.device = PushDevice.objects.create(
            user=self.citizen_user,
            token='firebase-token',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.announcement = Announcement.objects.create(
            author=self.staff_user,
            title='Comunicado com push',
            content='Conteudo para envio automatico',
            status=Announcement.STATUS_DRAFT,
        )

    def authenticate_as_staff(self):
        token = Token.objects.create(user=self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    @override_settings(PUSH_DISPATCH_ON_PUBLISH=True)
    @patch('api.delivery.PushNotificationService')
    def test_publish_dispatches_push_automatically(self, service_class):
        service = service_class.return_value
        service.dispatch_pending_for_announcement.return_value = {
            'configured': True,
            'sent': 1,
            'failed': 0,
            'pending': 0,
        }
        self.authenticate_as_staff()

        response = self.client.post(f'/api/announcements/{self.announcement.id}/publish/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service.dispatch_pending_for_announcement.assert_called_once()
        self.assertEqual(response.data['push_dispatch']['configured'], True)
        self.assertEqual(response.data['push_dispatch']['sent'], 1)
        self.assertEqual(response.data['push_dispatch']['skipped'], False)
        self.assertEqual(
            DeliveryLog.objects.filter(
                announcement=self.announcement,
                device=self.device,
            ).count(),
            1,
        )

    @override_settings(PUSH_DISPATCH_ON_PUBLISH=False)
    @patch('api.delivery.PushNotificationService')
    def test_publish_can_keep_push_pending_when_auto_dispatch_is_disabled(self, service_class):
        self.authenticate_as_staff()

        response = self.client.post(f'/api/announcements/{self.announcement.id}/publish/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_class.assert_not_called()
        self.assertEqual(response.data['push_dispatch']['skipped'], True)
        self.assertEqual(response.data['push_dispatch']['pending'], 1)
        self.assertEqual(
            DeliveryLog.objects.get(
                announcement=self.announcement,
                device=self.device,
            ).status,
            DeliveryLog.STATUS_PENDING,
        )

    @override_settings(
        PUSH_DISPATCH_ON_PUBLISH=True,
        PUSH_DISPATCH_ASYNC=True,
        CELERY_TASK_ALWAYS_EAGER=False,
    )
    @patch('api.tasks.process_announcement_deliveries.delay')
    def test_publish_queues_push_when_async_dispatch_is_enabled(self, delay):
        self.authenticate_as_staff()

        response = self.client.post(f'/api/announcements/{self.announcement.id}/publish/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        delay.assert_called_once_with(self.announcement.id)
        self.assertEqual(response.data['push_dispatch']['queued'], True)
        self.assertEqual(response.data['push_dispatch']['skipped'], False)
        self.assertEqual(
            DeliveryLog.objects.get(
                announcement=self.announcement,
                device=self.device,
            ).status,
            DeliveryLog.STATUS_PENDING,
        )


class SegmentDispatchTests(APITestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='gestor_segmento',
            email='gestor_segmento@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        self.citizen_a = User.objects.create_user(
            username='cidadao_segmento_a',
            email='cidadao_segmento_a@example.com',
            password='SenhaForte123',
        )
        self.citizen_b = User.objects.create_user(
            username='cidadao_segmento_b',
            email='cidadao_segmento_b@example.com',
            password='SenhaForte123',
        )
        self.device_a = PushDevice.objects.create(
            user=self.citizen_a,
            token='segment-device-a',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.device_b = PushDevice.objects.create(
            user=self.citizen_b,
            token='segment-device-b',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.anonymous_device = PushDevice.objects.create(
            token='segment-anonymous-device',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )

    def authenticate_as_staff(self):
        token = Token.objects.create(user=self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    def test_segment_endpoint_is_admin_only_and_creates_audit_log(self):
        anonymous_response = self.client.get('/api/segments/')
        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate_as_staff()
        response = self.client.post(
            '/api/segments/',
            {
                'name': 'Bairro Centro',
                'slug': 'bairro-centro',
                'description': 'Moradores do centro.',
                'users': [self.citizen_a.id],
                'push_devices': [self.anonymous_device.id],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        segment = Segment.objects.get(slug='bairro-centro')
        self.assertEqual(segment.users.count(), 1)
        self.assertEqual(segment.push_devices.count(), 1)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.staff_user,
                action='segment_created',
                target_id=str(segment.id),
            ).exists()
        )

    @override_settings(PUSH_DISPATCH_ON_PUBLISH=False)
    def test_segmented_announcement_delivers_only_to_segment_devices(self):
        segment = Segment.objects.create(
            name='Saude',
            slug='saude',
            description='Comunicados da saude.',
        )
        segment.users.add(self.citizen_a)
        segment.push_devices.add(self.anonymous_device)
        self.authenticate_as_staff()

        create_response = self.client.post(
            '/api/announcements/',
            {
                'title': 'Comunicado segmentado',
                'content': 'Somente para um segmento.',
                'status': Announcement.STATUS_DRAFT,
                'segments': [segment.id],
            },
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        publish_response = self.client.post(
            f'/api/announcements/{create_response.data["id"]}/publish/'
        )
        self.assertEqual(publish_response.status_code, status.HTTP_200_OK)

        announcement = Announcement.objects.get(id=create_response.data['id'])
        delivered_device_ids = set(
            DeliveryLog.objects
            .filter(announcement=announcement)
            .values_list('device_id', flat=True)
        )
        self.assertEqual(delivered_device_ids, {self.device_a.id, self.anonymous_device.id})
        self.assertEqual(publish_response.data['push_dispatch']['pending'], 2)

    @override_settings(PUSH_DISPATCH_ON_PUBLISH=False)
    def test_announcement_without_segments_delivers_to_all_active_devices(self):
        self.authenticate_as_staff()

        create_response = self.client.post(
            '/api/announcements/',
            {
                'title': 'Comunicado geral',
                'content': 'Para todos.',
                'status': Announcement.STATUS_DRAFT,
            },
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        publish_response = self.client.post(
            f'/api/announcements/{create_response.data["id"]}/publish/'
        )
        self.assertEqual(publish_response.status_code, status.HTTP_200_OK)

        announcement = Announcement.objects.get(id=create_response.data['id'])
        delivered_device_ids = set(
            DeliveryLog.objects
            .filter(announcement=announcement)
            .values_list('device_id', flat=True)
        )
        self.assertEqual(
            delivered_device_ids,
            {self.device_a.id, self.device_b.id, self.anonymous_device.id},
        )
        self.assertEqual(publish_response.data['push_dispatch']['pending'], 3)


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
            device=None,
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

    def test_admin_create_and_update_are_audited(self):
        self.client.force_login(self.admin_user)

        create_response = self.client.post(
            '/admin/api/institution/add/',
            {
                'name': 'Prefeitura Auditada',
                'kind': Institution.KIND_CITY_HALL,
                'official_email': 'gabinete@example.com',
                'phone_number': '51999999999',
                'is_active': 'on',
                '_save': 'Save',
            },
        )

        self.assertEqual(create_response.status_code, status.HTTP_302_FOUND)
        institution = Institution.objects.get(name='Prefeitura Auditada')
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.admin_user,
                action='admin_institution_created',
                target_id=str(institution.id),
            ).exists()
        )

        update_response = self.client.post(
            f'/admin/api/institution/{institution.id}/change/',
            {
                'name': 'Prefeitura Auditada Atualizada',
                'kind': Institution.KIND_CITY_HALL,
                'official_email': 'gabinete@example.com',
                'phone_number': '51999999999',
                'is_active': 'on',
                '_save': 'Save',
            },
        )

        self.assertEqual(update_response.status_code, status.HTTP_302_FOUND)
        institution.refresh_from_db()
        self.assertEqual(institution.name, 'Prefeitura Auditada Atualizada')
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.admin_user,
                action='admin_institution_updated',
                target_id=str(institution.id),
            ).exists()
        )

    def test_admin_action_deactivates_test_user_without_deleting_history(self):
        test_user = User.objects.create_user(
            username='usuario_teste_admin',
            email='usuario_teste_admin@example.com',
            password='SenhaForte123',
            is_staff=True,
        )
        token = Token.objects.create(user=test_user)
        device = PushDevice.objects.create(
            user=test_user,
            token='admin-test-user-device',
            platform=PushDevice.PLATFORM_WEB,
            is_active=True,
        )
        self.client.force_login(self.admin_user)

        response = self.client.post(
            '/admin/auth/user/',
            {
                'action': 'deactivate_selected_users',
                '_selected_action': [str(test_user.id), str(self.admin_user.id)],
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        test_user.refresh_from_db()
        self.admin_user.refresh_from_db()
        device.refresh_from_db()
        self.assertFalse(test_user.is_active)
        self.assertFalse(test_user.is_staff)
        self.assertFalse(test_user.is_superuser)
        self.assertFalse(Token.objects.filter(key=token.key).exists())
        self.assertFalse(device.is_active)
        self.assertTrue(self.admin_user.is_active)
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.admin_user,
                action='admin_user_deactivated',
                target_id=str(test_user.id),
            ).exists()
        )
