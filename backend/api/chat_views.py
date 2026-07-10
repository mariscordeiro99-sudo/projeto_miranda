from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework import parsers, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, Profile


FRONTEND_CURRENT_USER_ID = 'user-logado-123'
MAX_CHAT_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_CHAT_CONTENT_TYPES = {
    'application/pdf',
    'audio/mp3',
    'audio/mpeg',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'video/mp4',
}


def user_display_name(user):
    profile = getattr(user, 'profile', None)
    name = (user.first_name or '').strip()
    full_name = (user.get_full_name() or '').strip()
    phone = (getattr(profile, 'phone_number', '') or user.last_name or '').strip()

    if name:
        return name
    if phone and full_name.endswith(phone):
        name_without_phone = full_name[: -len(phone)].strip()
        if name_without_phone:
            return name_without_phone
    return full_name or user.username


def is_manager_user(user):
    profile = getattr(user, 'profile', None)
    return bool(
        user.is_staff
        or user.is_superuser
        or (profile and profile.role == Profile.ROLE_MANAGER)
    )


def user_role(user):
    return 'gestor' if is_manager_user(user) else 'colaborador'


def allowed_chat_contacts_for(user):
    queryset = (
        User.objects
        .select_related('profile')
        .filter(is_active=True)
        .exclude(id=user.id)
        .order_by('first_name', 'username')
    )

    if is_manager_user(user):
        return queryset

    return queryset.filter(
        Q(is_staff=True)
        | Q(is_superuser=True)
        | Q(profile__role=Profile.ROLE_MANAGER)
    ).distinct()


def can_chat_with(current_user, contact):
    if not contact or not contact.is_active or contact.id == current_user.id:
        return False

    return is_manager_user(current_user) or is_manager_user(contact)

def file_url(request, file_field):
    if not file_field:
        return None
    try:
        return request.build_absolute_uri(file_field.url)
    except (AttributeError, ValueError):
        return None


def file_download_url(request, file_field):
    return file_url(request, file_field)

def user_photo_url(request, user):
    profile = getattr(user, 'profile', None)
    if not profile or not profile.profile_picture:
        return None
    return file_url(request, profile.profile_picture)


def message_timestamp(value):
    if not value:
        return ''
    return timezone.localtime(value).strftime('%d/%m/%Y %H:%M')


def message_datetime(value):
    if not value:
        return None
    return timezone.localtime(value).isoformat()


def message_preview(message):
    if not message:
        return ''
    if message.message_type == ChatMessage.TYPE_TEXT:
        return message.text

    labels = {
        ChatMessage.TYPE_AUDIO: 'Áudio',
        ChatMessage.TYPE_IMAGE: 'Imagem',
        ChatMessage.TYPE_VIDEO: 'Vídeo',
        ChatMessage.TYPE_DOCUMENT: 'Documento',
    }
    return message.original_name or f'[{labels.get(message.message_type, "Arquivo")}]'


def serialize_message(request, message):
    is_sender = message.sender_id == request.user.id
    is_read = bool(message.read_at)
    delivery_status = 'lido' if is_sender and is_read else 'enviado' if is_sender else 'recebido'
    sender_id = (
        FRONTEND_CURRENT_USER_ID
        if is_sender
        else str(message.sender_id)
    )
    data = {
        'id': str(message.id),
        'senderId': sender_id,
        'texto': message.text,
        'timestamp': message_timestamp(message.created_at),
        'tipo': message.message_type,
        'status': delivery_status,
        'enviada': True,
        'lida': is_read,
        'createdAt': message_datetime(message.created_at),
        'readAt': message_datetime(message.read_at),
    }

    media_url = file_url(request, message.file)
    download_url = file_download_url(request, message.file)
    if media_url:
        data['midiaUrl'] = (
            download_url
            if message.message_type == ChatMessage.TYPE_DOCUMENT and download_url
            else media_url
        )
        data['downloadUrl'] = download_url or media_url
    if message.original_name:
        data['nomeArquivo'] = message.original_name

    return data


def get_contact(user_id, current_user):
    try:
        contact_id = int(user_id)
    except (TypeError, ValueError):
        return None

    contact = (
        User.objects
        .select_related('profile')
        .filter(id=contact_id, is_active=True)
        .exclude(id=current_user.id)
        .first()
    )

    if not can_chat_with(current_user, contact):
        return None

    return contact

def infer_message_type(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type.startswith('image/'):
        return ChatMessage.TYPE_IMAGE
    if content_type.startswith('video/'):
        return ChatMessage.TYPE_VIDEO
    if content_type.startswith('audio/'):
        return ChatMessage.TYPE_AUDIO
    return ChatMessage.TYPE_DOCUMENT


class ChatContactsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        contacts = allowed_chat_contacts_for(request.user)

        response_data = []
        for contact in contacts:
            conversation_filter = (
                Q(sender=request.user, receiver=contact)
                | Q(sender=contact, receiver=request.user)
            )
            last_message = (
                ChatMessage.objects
                .filter(conversation_filter)
                .order_by('-created_at')
                .first()
            )
            unread_count = ChatMessage.objects.filter(
                sender=contact,
                receiver=request.user,
                read_at__isnull=True,
            ).count()

            response_data.append({
                'id': str(contact.id),
                'nome': user_display_name(contact),
                'foto': user_photo_url(request, contact),
                'role': user_role(contact),
                'ultimaMensagem': message_preview(last_message),
                'timestampUltima': message_timestamp(last_message.created_at) if last_message else '',
                'naoLidas': unread_count,
                'ultimaMensagemStatus': (
                    'lido'
                    if last_message and last_message.sender_id == request.user.id and last_message.read_at
                    else 'enviado'
                    if last_message and last_message.sender_id == request.user.id
                    else 'recebido'
                    if last_message
                    else ''
                ),
                'ultimaMensagemLida': bool(
                    last_message
                    and last_message.sender_id == request.user.id
                    and last_message.read_at
                ),
                '_last_message_order': last_message.created_at if last_message else None,
            })

        response_data.sort(
            key=lambda item: (
                item['_last_message_order'] is None,
                -(item['_last_message_order'].timestamp()) if item['_last_message_order'] else 0,
                item['nome'].lower(),
            )
        )
        for item in response_data:
            item.pop('_last_message_order', None)

        return Response(response_data)


class ChatMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, contact_id, *args, **kwargs):
        contact = get_contact(contact_id, request.user)
        if not contact:
            return Response(
                {'detail': 'Contato não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        ChatMessage.objects.filter(
            sender=contact,
            receiver=request.user,
            read_at__isnull=True,
        ).update(read_at=timezone.now())

        messages = (
            ChatMessage.objects
            .filter(
                Q(sender=request.user, receiver=contact)
                | Q(sender=contact, receiver=request.user)
            )
            .order_by('created_at')
        )
        return Response([serialize_message(request, message) for message in messages])


class ChatMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, contact_id, *args, **kwargs):
        contact = get_contact(contact_id, request.user)
        if not contact:
            return Response(
                {'detail': 'Contato não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        updated = ChatMessage.objects.filter(
            sender=contact,
            receiver=request.user,
            read_at__isnull=True,
        ).update(read_at=timezone.now())

        return Response({
            'detail': 'Mensagens marcadas como lidas.',
            'total': updated,
        })


class ChatSendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        contact = get_contact(request.data.get('receiverId'), request.user)
        if not contact:
            return Response(
                {'detail': 'Contato não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        message_type = request.data.get('tipo') or ChatMessage.TYPE_TEXT
        if message_type != ChatMessage.TYPE_TEXT:
            return Response(
                {'detail': 'Envie arquivos pela rota de upload.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        text = str(request.data.get('texto') or '').strip()
        if not text:
            return Response(
                {'detail': 'Mensagem não pode ser vazia.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = ChatMessage.objects.create(
            sender=request.user,
            receiver=contact,
            text=text,
            message_type=ChatMessage.TYPE_TEXT,
        )
        return Response(serialize_message(request, message), status=status.HTTP_201_CREATED)


class ChatUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, *args, **kwargs):
        contact = get_contact(request.data.get('receiverId'), request.user)
        if not contact:
            return Response(
                {'detail': 'Contato não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'detail': 'Arquivo obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_type = getattr(uploaded_file, 'content_type', '') or ''
        if content_type not in ALLOWED_CHAT_CONTENT_TYPES:
            return Response(
                {'detail': f'Formato não suportado: {content_type or "desconhecido"}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file.size > MAX_CHAT_FILE_SIZE:
            return Response(
                {'detail': 'O arquivo excede o limite máximo de 50MB.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message_type = request.data.get('tipo') or infer_message_type(uploaded_file)
        valid_types = {
            ChatMessage.TYPE_AUDIO,
            ChatMessage.TYPE_IMAGE,
            ChatMessage.TYPE_VIDEO,
            ChatMessage.TYPE_DOCUMENT,
        }
        if message_type not in valid_types:
            message_type = infer_message_type(uploaded_file)

        message = ChatMessage.objects.create(
            sender=request.user,
            receiver=contact,
            message_type=message_type,
            file=uploaded_file,
            original_name=getattr(uploaded_file, 'name', '') or '',
        )
        return Response(serialize_message(request, message), status=status.HTTP_201_CREATED)
