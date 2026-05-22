import secrets

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import DocumentSerializer


class HelloView(APIView):
    def get(self, request):
        return Response({
            'message': 'Olá do backend Django! A comunicação está funcionando.',
            'status': 'healthy',
            'version': '1.0.0',
        })


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '')
        phone = request.data.get('telefone', '') or request.data.get('phone_number', '')
        is_gestor = str(request.data.get('isGestor', '') or request.data.get('is_gestor', '')).lower() in ('true', '1', 'yes')

        if not username or not email or not password:
            return Response(
                {'detail': 'username, email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'detail': 'username already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'email already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=phone,
            is_staff=is_gestor,
        )
        user.set_password(password)
        user.save()

        return Response(
            {
                'message': 'User registered successfully.',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args, **kwargs):
        login_value = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not login_value or not password:
            return Response(
                {'detail': 'username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = None
        password_is_valid = False
        if '@' in login_value:
            user = User.objects.filter(email__iexact=login_value).first()
            password_is_valid = bool(user and user.is_active and user.check_password(password))
        elif login_value.isdigit():
            user = User.objects.filter(last_name=login_value).first()
            password_is_valid = bool(user and user.is_active and user.check_password(password))
        else:
            user = authenticate(request, username=login_value, password=password)
            password_is_valid = user is not None

        if not password_is_valid:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = secrets.token_urlsafe(32)
        return Response(
            {
                'access_token': token,
                'token_type': 'bearer',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                },
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        identifier = request.data.get('email', '') or request.data.get('username', '')
        identifier = identifier.strip()

        if not identifier:
            return Response(
                {'detail': 'email is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=identifier).first()
        if user and user.is_active and user.email:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
            reset_url = f'{frontend_url}/reset-password?uid={uid}&token={token}'

            send_mail(
                subject='Redefinicao de senha - Projeto Miranda',
                message=(
                    'Recebemos uma solicitacao para redefinir sua senha.\n\n'
                    f'Acesse este link para criar uma nova senha:\n{reset_url}\n\n'
                    'Se voce nao solicitou isso, ignore este e-mail.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response(
            {'detail': 'If the account exists, a password reset email was sent.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '') or request.data.get('password', '')

        if not uid or not token or not new_password:
            return Response(
                {'detail': 'uid, token and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, UnicodeDecodeError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Invalid or expired password reset token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=user)
        except ValidationError as error:
            return Response(
                {'detail': list(error.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response(
            {'detail': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK,
        )


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
