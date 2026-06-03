import os
import uuid
from pathlib import PurePosixPath

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.text import get_valid_filename


IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
VIDEO_TYPES = {'video/mp4', 'video/quicktime', 'video/webm'}


def _clean_path(name):
    parts = []
    for part in str(name).replace('\\', '/').split('/'):
        if not part or part in {'.', '..'}:
            continue
        parts.append(get_valid_filename(part))
    return '/'.join(parts)


def _with_base_folder(name):
    base_folder = getattr(settings, 'CLOUDINARY_MEDIA_FOLDER', '').strip('/')
    if not base_folder:
        return name
    return f'{base_folder}/{name.lstrip("/")}'


def _split_name(name):
    name = str(name).replace('\\', '/')
    parts = name.split('/', 1)
    if len(parts) == 2 and parts[0] in {'image', 'video', 'raw'}:
        resource_type, public_name = parts
    else:
        resource_type, public_name = 'image', name

    stem, extension = os.path.splitext(public_name)
    if resource_type == 'raw':
        return resource_type, public_name, ''
    return resource_type, stem, extension.lstrip('.')


def _unique_public_id(name, resource_type):
    path = PurePosixPath(name)
    suffix = uuid.uuid4().hex
    if resource_type == 'raw':
        return str(path.with_name(f'{path.stem}_{suffix}{path.suffix}'))
    return str(path.with_name(f'{path.stem}_{suffix}'))


class CloudinaryMediaStorage(Storage):
    """Django media storage for images, videos and raw files in Cloudinary."""

    def _resource_type(self, content):
        content_type = getattr(content, 'content_type', '') or ''
        if content_type in IMAGE_TYPES or content_type.startswith('image/'):
            return 'image'
        if content_type in VIDEO_TYPES or content_type.startswith('video/'):
            return 'video'
        return 'raw'

    def _save(self, name, content):
        name = _with_base_folder(_clean_path(name))
        resource_type = self._resource_type(content)
        public_id = _unique_public_id(name, resource_type)

        if hasattr(content, 'seek'):
            content.seek(0)

        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            resource_type=resource_type,
            overwrite=False,
            invalidate=True,
            use_filename=False,
            unique_filename=False,
        )

        stored_name = f'{resource_type}/{result["public_id"]}'
        result_format = result.get('format')
        if resource_type != 'raw' and result_format:
            stored_name = f'{stored_name}.{result_format}'
        return stored_name

    def _open(self, name, mode='rb'):
        raise NotImplementedError('Cloudinary media files are served by URL.')

    def exists(self, name):
        return False

    def delete(self, name):
        resource_type, public_id, _ = _split_name(name)
        cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type,
            invalidate=True,
        )

    def url(self, name):
        resource_type, public_id, file_format = _split_name(name)
        url, _ = cloudinary_url(
            public_id,
            resource_type=resource_type,
            format=file_format or None,
            secure=True,
        )
        return url

    def size(self, name):
        resource_type, public_id, _ = _split_name(name)
        resource = cloudinary.api.resource(public_id, resource_type=resource_type)
        return resource.get('bytes', 0)
