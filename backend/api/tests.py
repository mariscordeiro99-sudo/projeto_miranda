import struct
import tempfile
from shutil import rmtree

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APITestCase

from .models import Profile
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
