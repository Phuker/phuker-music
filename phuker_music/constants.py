#!/usr/bin/env python3
# encoding: utf-8


AUDIO_EXT_LIST: tuple[str, ...] = (
    '.flac',
    '.m4a',
    '.mp3',
    '.ogg',
    '.wav',
    '.weba',
)

# https://developer.mozilla.org/zh-CN/docs/Web/Media/Guides/Formats/Image_types
IMAGE_EXT_LIST: tuple[str, ...] = (
    '.apng',
    '.avif',
    '.bmp',
    '.cur',
    '.gif',
    '.ico',
    '.jfif',
    '.jif',
    '.jpe',
    '.jpeg',
    '.jpg',
    '.pjp',
    '.pjpeg',
    '.png',
    '.svg',
    '.tif',
    '.tiff',
    '.webp',
)

# album_config
CHOICES_SORT_TYPE: tuple[str, ...] = ('filename', 'mtime_desc')
DEFAULT_SORT_TYPE: str = 'filename'
DEFAULT_PLAYER_FILENAME: str = 'player.html'

# albums_config
DEFAULT_ALBUMS_DIR_PATH: str = '.'
DEFAULT_ALBUMS_INDEX_FILENAME: str = 'index.html'

# albums_webui
DEFAULT_WEBUI_HOST: str = '127.0.0.1'
DEFAULT_WEBUI_PORT: int = 8000
DEFAULT_WEBUI_TRUSTED_HOSTS: list[str] = [
    '127.0.0.1',
    'localhost',
]
