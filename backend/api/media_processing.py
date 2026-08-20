import logging
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import get_valid_filename
from rest_framework.exceptions import ValidationError as DRFValidationError

from .media_validation import get_ffmpeg_executable, validate_attachment


logger = logging.getLogger(__name__)


def prepare_attachment(uploaded_file):
    """Valida um anexo e otimiza vídeos antes do armazenamento definitivo."""
    validate_attachment(uploaded_file)
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if not content_type.startswith('video/'):
        return uploaded_file

    if not getattr(settings, 'VIDEO_COMPRESSION_ENABLED', True):
        return uploaded_file

    return compress_video(uploaded_file)


def compress_video(uploaded_file):
    ffmpeg_path = get_ffmpeg_executable()
    if not ffmpeg_path:
        raise DRFValidationError(
            'A compressão de vídeo está indisponível. O FFmpeg não foi encontrado.'
        )

    input_suffix = Path(getattr(uploaded_file, 'name', 'video')).suffix or '.video'
    output_name = compressed_video_name(getattr(uploaded_file, 'name', 'video'))

    with tempfile.TemporaryDirectory(prefix='miranda-video-') as temp_dir:
        input_path = Path(temp_dir) / f'input{input_suffix}'
        output_path = Path(temp_dir) / output_name
        write_uploaded_file(uploaded_file, input_path)

        command = build_ffmpeg_command(ffmpeg_path, input_path, output_path)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=getattr(settings, 'VIDEO_COMPRESSION_TIMEOUT_SECONDS', 180),
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise DRFValidationError(
                'A compressão do vídeo excedeu o tempo limite. Tente um arquivo menor.'
            ) from error
        except OSError as error:
            raise DRFValidationError(
                'Não foi possível iniciar a compressão do vídeo.'
            ) from error

        if result.returncode != 0 or not output_path.exists():
            logger.warning(
                'Falha na compressão de vídeo.',
                extra={
                    'original_name': getattr(uploaded_file, 'name', ''),
                    'ffmpeg_error': last_error_line(result.stderr),
                },
            )
            raise DRFValidationError('Não foi possível comprimir o vídeo enviado.')

        output_size = output_path.stat().st_size
        if output_size <= 0:
            raise DRFValidationError('A compressão gerou um arquivo de vídeo vazio.')

        max_output_size = getattr(
            settings,
            'MAX_COMPRESSED_VIDEO_SIZE',
            60 * 1024 * 1024,
        )
        if output_size > max_output_size:
            raise DRFValidationError(
                'O vídeo permaneceu acima do limite permitido mesmo após a compressão.'
            )

        return SimpleUploadedFile(
            output_name,
            output_path.read_bytes(),
            content_type='video/mp4',
        )


def build_ffmpeg_command(ffmpeg_path, input_path, output_path):
    max_dimension = max(
        320,
        int(getattr(settings, 'VIDEO_COMPRESSION_MAX_DIMENSION', 1280)),
    )
    crf = min(
        35,
        max(18, int(getattr(settings, 'VIDEO_COMPRESSION_CRF', 28))),
    )
    preset = getattr(settings, 'VIDEO_COMPRESSION_PRESET', 'medium')
    audio_bitrate = getattr(settings, 'VIDEO_COMPRESSION_AUDIO_BITRATE', '96k')
    scale_filter = (
        "scale=w='if(gt(iw,ih),min(iw,"
        f"{max_dimension}),-2)':h='if(gt(iw,ih),-2,min(ih,{max_dimension}))'"
    )

    return [
        str(ffmpeg_path),
        '-y',
        '-i',
        str(input_path),
        '-map',
        '0:v:0',
        '-map',
        '0:a?',
        '-map_metadata',
        '-1',
        '-vf',
        scale_filter,
        '-c:v',
        'libx264',
        '-preset',
        str(preset),
        '-crf',
        str(crf),
        '-pix_fmt',
        'yuv420p',
        '-c:a',
        'aac',
        '-b:a',
        str(audio_bitrate),
        '-movflags',
        '+faststart',
        str(output_path),
    ]


def write_uploaded_file(uploaded_file, destination):
    original_position = None
    if hasattr(uploaded_file, 'tell'):
        try:
            original_position = uploaded_file.tell()
        except (OSError, ValueError):
            original_position = None

    if hasattr(uploaded_file, 'seek'):
        uploaded_file.seek(0)

    try:
        with destination.open('wb') as output:
            chunks = getattr(uploaded_file, 'chunks', None)
            if callable(chunks):
                for chunk in chunks():
                    output.write(chunk)
            else:
                output.write(uploaded_file.read())
    finally:
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(original_position or 0)


def compressed_video_name(original_name):
    stem = Path(original_name or 'video').stem
    safe_stem = get_valid_filename(stem) or 'video'
    return f'{safe_stem}.mp4'


def last_error_line(stderr):
    lines = [line.strip() for line in (stderr or '').splitlines() if line.strip()]
    if not lines:
        return ''
    return lines[-1][:300]
