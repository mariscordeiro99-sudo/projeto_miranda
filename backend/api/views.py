import secrets

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
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
        login_value = request.data.get('username', '')
        password = request.data.get('password', '')

        if not login_value or not password:
            return Response(
                {'detail': 'username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if '@' in login_value:
            user = User.objects.filter(email__iexact=login_value).first()
            if user:
                login_value = user.username

        user = authenticate(request, username=login_value, password=password)

        if user is None:
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


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
