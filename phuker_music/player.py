#!/usr/bin/env python3
# encoding: utf-8

import os
import logging
import math
import pathlib
import hashlib
import json

import mutagen

from . import _utils


logger: logging.Logger = logging.getLogger(__name__)

AUDIO_EXT_LIST: tuple[str, ...] = (
    '.mp3',
    '.ogg',
    '.flac',
    '.m4a',
    '.wav',
    '.weba',
)


def match_ext_list(file_path: str, ext_list: tuple[str, ...]) -> bool:
    return os.path.splitext(file_path)[1].lower() in ext_list


def get_file_size_str(file_path: str) -> str:
    size_suffix_list = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

    file_size = os.stat(file_path).st_size
    if file_size == 0:
        return '0 B'

    size_suffix_index = math.floor(math.log(file_size, 1024))
    if size_suffix_index == 0:
        return f'{file_size} B'
    else:
        return f'{file_size / (1024 ** size_suffix_index):.2f} {size_suffix_list[size_suffix_index]}'


def get_duration_str(duration: int) -> str:
    seconds = duration % 60
    duration //= 60
    minutes = duration % 60
    hours = duration // 60

    if hours > 0:
        return f'{hours}:{minutes:02d}:{seconds:02d}'
    else:
        return f'{minutes}:{seconds:02d}'


def get_file_duration_str(file_path: str) -> str:
    audio = mutagen.File(file_path)
    if audio is None:
        return ''

    duration = math.floor(audio.info.length)
    result = get_duration_str(duration)

    return result


def get_music_groups(album_dir_path: str, recursively: bool = False, sort_type: str = 'filename') -> list[dict[str, object]]:
    result = []
    index = -1
    for top, dirnames, filenames in os.walk(album_dir_path):
        top_rel_path = os.path.relpath(top, album_dir_path)
        if top_rel_path == '.':
            top_rel_path = ''

        # The list is in arbitrary order
        # https://stackoverflow.com/questions/18282370/in-what-order-does-os-walk-iterates-iterate
        dirnames.sort()

        filenames = [filename for filename in filenames if match_ext_list(filename, AUDIO_EXT_LIST)]
        if sort_type == 'filename':
            filenames.sort()
        elif sort_type == 'mtime_desc':
            filenames.sort(key=lambda filename: (-os.path.getmtime(os.path.join(top, filename)), filename))
        else:
            raise ValueError(f'Invalid sort_type: {sort_type!r}')

        music_info_sub_list = []
        for filename in filenames:
            index += 1
            filename_stem = pathlib.PurePosixPath(filename).stem
            file_abs_path = os.path.join(top, filename)
            file_rel_path = os.path.join(top_rel_path, filename)
            file_size_str = get_file_size_str(file_abs_path)
            duration_str = get_file_duration_str(file_abs_path)
            music_info_sub_list.append({
                'index': index,
                'path': file_rel_path.replace(os.sep, '/'),
                'name': filename_stem,
                'file_size_str': file_size_str,
                'duration_str': duration_str,
            })

        if music_info_sub_list:
            result.append({
                'name': top_rel_path.replace(os.sep, '/'),
                'music_info_sub_list': music_info_sub_list,
            })

        if not recursively:
            break

    return result


def get_hash(s: str) -> str:
    return hashlib.sha256(s.encode('UTF-8')).hexdigest()[:16]


def generate(*, album_dir_path: str, title: str | None = None, cover_file: str | None = None, output_filename: str = 'player.html', recursively: bool = False, sort_type: str = 'filename', overwrite: bool = False) -> None:
    # album_dir_path must be abs path, without trailing sep char
    _utils._assert(album_dir_path and album_dir_path[-1] not in ('/', '\\'), f'Invalid album_dir_path')
    _utils._assert('/' not in output_filename and '\\' not in output_filename, f'output_filename must not contain path separators: {output_filename!r}')

    if not title:
        title = os.path.basename(album_dir_path)

    if cover_file:
        _cover_file_path = os.path.join(album_dir_path, cover_file)
        if not os.path.isfile(_cover_file_path):
            raise FileNotFoundError(f'Cover file does not exist: {_cover_file_path!r}')

        # normalize, add './'
        cover_file = './' + os.path.relpath(_cover_file_path, album_dir_path).replace(os.sep, '/')

    logger.info('Generating player in: %r', album_dir_path)

    music_info_groups = get_music_groups(album_dir_path, recursively, sort_type)
    music_info_list = [music_info for group in music_info_groups for music_info in group['music_info_sub_list']]
    logger.info('Found %d groups, %d files', len(music_info_groups), len(music_info_list))
    logger.debug('music_info_groups: %s', json.dumps(music_info_groups, indent=4, ensure_ascii=False))
    logger.debug('music_info_list: %s', json.dumps(music_info_list, indent=4, ensure_ascii=False))

    lang = _utils.detect_language(' '.join([title] + [_['name'] for _ in music_info_list]))

    # use os.path.basename() to get same result for same dir name, which may sync between computers
    storage_key_prefix = f'music_{get_hash(os.path.basename(album_dir_path))}_'

    env = _utils.get_jinja_env()
    template = env.get_template('player.html')
    result = template.render(lang=lang, title=title, cover_file=cover_file, music_info_groups=music_info_groups, music_info_list=music_info_list, storage_key_prefix=storage_key_prefix)

    output_file_path = os.path.join(album_dir_path, output_filename)
    if os.path.exists(output_file_path) and not overwrite:
        raise FileExistsError(f'Output file already exists: {output_file_path!r}, use -f/--force to overwrite')

    logger.info('Writing to file: %r', output_file_path)
    with open(output_file_path, 'w', encoding='UTF-8') as f:
        f.write(result)
