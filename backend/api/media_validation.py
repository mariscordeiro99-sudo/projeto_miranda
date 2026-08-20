import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import Attachment


class VideoDurationValidationError(Exception):
    pass


MAX_ATTACHMENT_SIZE = 60 * 1024 * 1024
MAX_VIDEO_SOURCE_SIZE = 250 * 1024 * 1024
MAX_VIDEO_DURATION_SECONDS = 60
MAX_PROFILE_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VISUAL_IDENTITY_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_PROFILE_IMAGE_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
}
ALLOWED_VISUAL_IDENTITY_IMAGE_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
}
ALLOWED_ATTACHMENT_CONTENT_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'video/mp4',
}


def attachment_type(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type.startswith('image/'):
        return Attachment.TYPE_IMAGE
    if content_type.startswith('video/'):
        return Attachment.TYPE_VIDEO
    if content_type == 'application/pdf':
        return Attachment.TYPE_DOCUMENT
    return Attachment.TYPE_OTHER


def validate_attachment(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type not in ALLOWED_ATTACHMENT_CONTENT_TYPES:
        raise DRFValidationError(
            f'Tipo de anexo não suportado: {content_type or "desconhecido"}.'
        )
    if content_type.startswith('video/'):
        if uploaded_file.size > MAX_VIDEO_SOURCE_SIZE:
            raise DRFValidationError('O vídeo original excede o limite de 250MB.')
        try:
            validate_video_duration(uploaded_file, MAX_VIDEO_DURATION_SECONDS)
        except VideoDurationValidationError as error:
            raise DRFValidationError(str(error))
        return

    if uploaded_file.size > MAX_ATTACHMENT_SIZE:
        raise DRFValidationError('O anexo excede o limite de 60MB.')


def validate_profile_picture(uploaded_file):
    if not uploaded_file:
        return

    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type not in ALLOWED_PROFILE_IMAGE_CONTENT_TYPES:
        raise DRFValidationError('A foto de perfil deve ser JPG, PNG ou WEBP.')

    if uploaded_file.size > MAX_PROFILE_IMAGE_SIZE:
        raise DRFValidationError('A foto de perfil deve ter no máximo 10MB.')


def validate_visual_identity_image(uploaded_file):
    if not uploaded_file:
        return

    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type not in ALLOWED_VISUAL_IDENTITY_IMAGE_CONTENT_TYPES:
        raise DRFValidationError('O brasao deve ser JPG, PNG ou WEBP.')

    if uploaded_file.size > MAX_VISUAL_IDENTITY_IMAGE_SIZE:
        raise DRFValidationError('O brasao deve ter no maximo 10MB.')


def validate_video_duration(uploaded_file, max_seconds):
    duration = get_video_duration(uploaded_file)
    if duration is None:
        raise VideoDurationValidationError(
            'Não foi possível validar a duração do vídeo. Envie um arquivo MP4/MOV válido.'
        )

    if duration > max_seconds:
        raise VideoDurationValidationError(
            f'O vídeo deve ter no máximo {max_seconds} segundos.'
        )


def get_video_duration(uploaded_file):
    duration = _get_duration_with_ffprobe(uploaded_file)
    if duration is not None:
        return duration

    duration = _get_mp4_duration(_read_uploaded_file(uploaded_file))
    if duration is not None:
        return duration

    return _get_duration_with_ffmpeg(uploaded_file)


def _read_uploaded_file(uploaded_file):
    position = None
    if hasattr(uploaded_file, 'tell'):
        try:
            position = uploaded_file.tell()
        except (OSError, ValueError):
            position = None

    if hasattr(uploaded_file, 'seek'):
        uploaded_file.seek(0)

    data = uploaded_file.read()

    if hasattr(uploaded_file, 'seek'):
        uploaded_file.seek(position or 0)

    return data


def _get_duration_with_ffprobe(uploaded_file):
    ffprobe_path = shutil.which('ffprobe')
    if not ffprobe_path:
        return None

    temp_path = None
    try:
        temporary_file_path = getattr(uploaded_file, 'temporary_file_path', None)
        if callable(temporary_file_path):
            temp_path = temporary_file_path()
            return _run_ffprobe(ffprobe_path, temp_path)

        suffix = os.path.splitext(getattr(uploaded_file, 'name', 'upload'))[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(_read_uploaded_file(uploaded_file))
            temp_path = temp_file.name

        return _run_ffprobe(ffprobe_path, temp_path)
    finally:
        if temp_path and not callable(getattr(uploaded_file, 'temporary_file_path', None)):
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def _run_ffprobe(ffprobe_path, file_path):
    result = subprocess.run(
        [
            ffprobe_path,
            '-v',
            'error',
            '-show_entries',
            'format=duration',
            '-of',
            'json',
            file_path,
        ],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if result.returncode != 0:
        return None

    try:
        duration = json.loads(getattr(result, 'stdout', '') or '')['format']['duration']
        return float(duration)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _get_duration_with_ffmpeg(uploaded_file):
    ffmpeg_path = get_ffmpeg_executable()
    if not ffmpeg_path:
        return None

    temp_path = None
    try:
        temporary_file_path = getattr(uploaded_file, 'temporary_file_path', None)
        if callable(temporary_file_path):
            return _run_ffmpeg_probe(ffmpeg_path, temporary_file_path())

        suffix = os.path.splitext(getattr(uploaded_file, 'name', 'upload'))[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(_read_uploaded_file(uploaded_file))
            temp_path = temp_file.name

        return _run_ffmpeg_probe(ffmpeg_path, temp_path)
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def _run_ffmpeg_probe(ffmpeg_path, file_path):
    try:
        result = subprocess.run(
            [
                ffmpeg_path,
                '-hide_banner',
                '-i',
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    match = re.search(
        r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)',
        result.stderr or '',
    )
    if not match:
        return None

    hours, minutes, seconds = match.groups()
    return (int(hours) * 3600) + (int(minutes) * 60) + float(seconds)


def get_ffmpeg_executable():
    configured_path = getattr(settings, 'FFMPEG_BINARY', '').strip()
    if configured_path:
        resolved_path = shutil.which(configured_path)
        if resolved_path:
            return resolved_path
        if Path(configured_path).is_file():
            return configured_path

    system_path = shutil.which('ffmpeg')
    if system_path:
        return system_path

    try:
        import imageio_ffmpeg

        bundled_path = imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError, OSError):
        return None

    return bundled_path if bundled_path and Path(bundled_path).is_file() else None


def _get_mp4_duration(data):
    return _find_mvhd_duration(data, 0, len(data), depth=0)


def _find_mvhd_duration(data, start, end, depth):
    if depth > 8:
        return None

    for atom_type, payload_start, atom_end in _iter_mp4_atoms(data, start, end):
        if atom_type == b'mvhd':
            return _parse_mvhd_duration(data[payload_start:atom_end])

        if atom_type in {b'moov', b'trak', b'mdia', b'minf', b'stbl', b'edts', b'udta'}:
            duration = _find_mvhd_duration(data, payload_start, atom_end, depth + 1)
            if duration is not None:
                return duration

    return None


def _iter_mp4_atoms(data, start, end):
    offset = start
    while offset + 8 <= end:
        size = struct.unpack('>I', data[offset:offset + 4])[0]
        atom_type = data[offset + 4:offset + 8]
        header_size = 8

        if size == 1:
            if offset + 16 > end:
                return
            size = struct.unpack('>Q', data[offset + 8:offset + 16])[0]
            header_size = 16
        elif size == 0:
            size = end - offset

        if size < header_size:
            return

        atom_end = offset + size
        if atom_end > end:
            return

        yield atom_type, offset + header_size, atom_end
        offset = atom_end


def _parse_mvhd_duration(payload):
    version = payload[0] if payload else None

    if version == 0 and len(payload) >= 20:
        timescale = struct.unpack('>I', payload[12:16])[0]
        duration = struct.unpack('>I', payload[16:20])[0]
    elif version == 1 and len(payload) >= 32:
        timescale = struct.unpack('>I', payload[20:24])[0]
        duration = struct.unpack('>Q', payload[24:32])[0]
    else:
        return None

    if timescale == 0:
        return None

    return duration / timescale
