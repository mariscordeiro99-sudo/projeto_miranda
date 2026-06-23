import cloudinary.exceptions
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import parsers, serializers, status, throttling
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import issue_auth_token, manager_token_ttl_seconds
from .media_validation import validate_profile_picture
from .models import Profile


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'auth_register'
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        request=inline_serializer(
            name='RegisterRequest',
            fields={
                'username': serializers.CharField(),
                'email': serializers.EmailField(),
                'password': serializers.CharField(write_only=True),
                'first_name': serializers.CharField(required=False, allow_blank=True),
                'phone_number': serializers.CharField(required=False, allow_blank=True),
                'telefone': serializers.CharField(required=False, allow_blank=True),
                'is_gestor': serializers.BooleanField(required=False),
                'isGestor': serializers.BooleanField(required=False),
                'profile_picture': serializers.ImageField(required=False),
            },
        ),
        responses=inline_serializer(
            name='RegisterResponse',
            fields={
                'message': serializers.CharField(),
                'user': serializers.DictField(),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '')
        phone = request.data.get('telefone', '') or request.data.get('phone_number', '')
        profile_picture = request.FILES.get('profile_picture')
        requested_manager_access = str(
            request.data.get('isGestor', '') or request.data.get('is_gestor', '')
        ).lower() in ('true', '1', 'yes')

        if not username or not email or not password:
            return Response(
                {'detail': 'Usuário, e-mail e senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_profile_picture(profile_picture)
        except DRFValidationError as error:
            detail = error.detail[0] if isinstance(error.detail, list) else error.detail
            return Response(
                {'detail': str(detail)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_users = list(
            User.objects
            .filter(Q(username=username) | Q(email=email))
            .values('username', 'email')[:2]
        )

        if any(user['username'] == username for user in existing_users):
            return Response(
                {'detail': 'Este usuário já existe.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if any(user['email'] == email for user in existing_users):
            return Response(
                {'detail': 'Este e-mail já existe.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidate_user = User(username=username, email=email, first_name=first_name)
        try:
            validate_password(password, user=candidate_user)
        except ValidationError as error:
            return Response(
                {'detail': list(error.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=phone,
                    is_staff=False,
                )
                user.set_password(password)
                user.save()
                Profile.objects.create(
                    user=user,
                    phone_number=phone,
                    role=Profile.ROLE_CITIZEN,
                    manager_access_requested=requested_manager_access,
                    profile_picture=profile_picture,
                )
        except cloudinary.exceptions.Error:
            return Response(
                {'detail': 'Não foi possível enviar a foto de perfil. Tente novamente.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        message = 'Usuário cadastrado com sucesso.'
        if requested_manager_access:
            message = 'Cadastro realizado. O acesso de gestor aguarda aprovação.'

        return Response(
            {
                'message': message,
                'manager_access_status': (
                    'pending' if requested_manager_access else 'not_requested'
                ),
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
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'auth_login'

    @extend_schema(
        request=inline_serializer(
            name='LoginRequest',
            fields={
                'username': serializers.CharField(),
                'password': serializers.CharField(write_only=True),
            },
        ),
        responses=inline_serializer(
            name='LoginResponse',
            fields={
                'access_token': serializers.CharField(),
                'token': serializers.CharField(),
                'token_type': serializers.CharField(),
                'expires_in': serializers.IntegerField(required=False, allow_null=True),
                'user': serializers.DictField(),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        login_value = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not login_value or not password:
            return Response(
                {'detail': 'Usuário e senha são obrigatórios.'},
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
                {'detail': 'Credenciais inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        profile = getattr(user, 'profile', None)
        role = profile.role if profile else Profile.ROLE_CITIZEN
        permissions_data = {
            'controlAcess': bool(profile and profile.can_control_access),
            'announcement': bool(profile and profile.can_manage_announcements),
            'idtVisual': bool(profile and profile.can_manage_visual_identity),
            'dashboardGestor': bool(
                profile and profile.can_view_manager_dashboard
            ),
        }
        permissions_data['isAdmin'] = all(permissions_data.values())

        token = issue_auth_token(user)
        token_expires_in = manager_token_ttl_seconds(user)
        return Response(
            {
                'access_token': token.key,
                'token': token.key,
                'token_type': 'bearer',
                'expires_in': token_expires_in,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'role_code': role,
                    'role': (
                        'gestor'
                        if role == Profile.ROLE_MANAGER
                        else 'colaborador'
                    ),
                    'roleAtual': (
                        'gestor'
                        if role == Profile.ROLE_MANAGER
                        else 'colaborador'
                    ),
                    'manager_access_requested': bool(
                        profile and profile.manager_access_requested
                    ),
                    'permissoes': permissions_data,
                },
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'password_reset'

    @extend_schema(
        request=inline_serializer(
            name='PasswordResetRequestPayload',
            fields={
                'email': serializers.EmailField(required=False),
                'username': serializers.CharField(required=False),
            },
        ),
        responses=inline_serializer(
            name='PasswordResetRequestResponse',
            fields={'detail': serializers.CharField()},
        ),
    )
    def post(self, request, *args, **kwargs):
        identifier = request.data.get('email', '') or request.data.get('username', '')
        identifier = identifier.strip()

        if not identifier:
            return Response(
                {'detail': 'E-mail ou usuário é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=identifier).first()
        if user and user.is_active and user.email:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
            reset_url = f'{frontend_url}/reset-password?uid={uid}&token={token}'

            send_mail(
                subject='Redefinição de senha - Projeto Miranda',
                message=(
                    'Recebemos uma solicitação para redefinir sua senha.\n\n'
                    f'Acesse este link para criar uma nova senha:\n{reset_url}\n\n'
                    'Se você não solicitou isso, ignore este e-mail.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response(
            {'detail': 'Se a conta existir, um e-mail de redefinição de senha foi enviado.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'password_reset'

    @extend_schema(
        request=inline_serializer(
            name='PasswordResetConfirmRequest',
            fields={
                'uid': serializers.CharField(),
                'token': serializers.CharField(),
                'new_password': serializers.CharField(write_only=True, required=False),
                'password': serializers.CharField(write_only=True, required=False),
            },
        ),
        responses=inline_serializer(
            name='PasswordResetConfirmResponse',
            fields={'detail': serializers.CharField()},
        ),
    )
    def post(self, request, *args, **kwargs):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '') or request.data.get('password', '')

        if not uid or not token or not new_password:
            return Response(
                {'detail': 'UID, token e nova senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, UnicodeDecodeError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Token de redefinição de senha inválido ou expirado.'},
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
        Token.objects.filter(user=user).delete()

        return Response(
            {'detail': 'Senha redefinida com sucesso.'},
            status=status.HTTP_200_OK,
        )
