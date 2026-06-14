#!/usr/bin/env python3
# encoding: utf-8

import os
import logging
import math
import pathlib
import hashlib
import json

import mutagen

from . import constants
from . import utils
from .utils import os_path


logger: logging.Logger = logging.getLogger(__name__)


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
        top = top.replace(os.sep, '/')
        top_rel_path = os_path.relpath(top, album_dir_path)
        if top_rel_path == '.':
            top_rel_path = ''

        # The list is in arbitrary order
        # https://stackoverflow.com/questions/18282370/in-what-order-does-os-walk-iterates-iterate
        dirnames.sort()

        filenames = [filename for filename in filenames if utils.match_ext_list(filename, constants.AUDIO_EXT_LIST)]
        if sort_type == 'filename':
            filenames.sort()
        elif sort_type == 'mtime_desc':
            filenames.sort(key=lambda filename: (-os_path.getmtime(os_path.join(top, filename)), filename))
        else:
            raise ValueError(f'Invalid sort_type: {sort_type!r}')

        music_info_sub_list = []
        for filename in filenames:
            index += 1
            filename_stem = pathlib.PurePosixPath(filename).stem
            file_abs_path = os_path.join(top, filename)
            file_rel_path = os_path.join(top_rel_path, filename)
            file_size_str = get_file_size_str(file_abs_path)
            duration_str = get_file_duration_str(file_abs_path)
            music_info_sub_list.append({
                'index': index,
                'path': file_rel_path,
                'name': filename_stem,
                'file_size_str': file_size_str,
                'duration_str': duration_str,
            })

        if music_info_sub_list:
            result.append({
                'name': top_rel_path,
                'music_info_sub_list': music_info_sub_list,
            })

        if not recursively:
            break

    return result


def get_hash(s: str) -> str:
    return hashlib.sha256(s.encode('UTF-8')).hexdigest()[:16]


def normalize_album_config(album_config_input: dict, *, base_dir_path: str = '.', is_abs_path: bool = True) -> dict:
    album_config = {
        'album_dir_path': None,
        'title': None,
        'cover_file': None,
        'output_filename': 'player.html',
        'recursively': False,
        'sort_type': 'filename',
    }
    album_config.update(album_config_input)

    utils.assert_(isinstance(album_config['album_dir_path'], str) and album_config['album_dir_path'], f'invalid album_dir_path: {album_config["album_dir_path"]!r}')
    utils.assert_(isinstance(album_config['title'], (str, type(None))), f'invalid album_config: {album_config!r}')
    utils.assert_(isinstance(album_config['cover_file'], (str, type(None))), f'invalid album_config: {album_config!r}')
    utils.assert_(isinstance(album_config['output_filename'], str), f'invalid album_config: {album_config!r}')
    utils.assert_('/' not in album_config['output_filename'] and '\\' not in album_config['output_filename'], f'output_filename must not contain path separators: {album_config["output_filename"]!r}')
    utils.assert_(isinstance(album_config['recursively'], bool), f'invalid album_config: {album_config!r}')
    utils.assert_(isinstance(album_config['sort_type'], str), f'invalid album_config: {album_config!r}')

    album_dir_path = utils.get_abs_joined_path(base_dir_path, album_config['album_dir_path'])
    utils.assert_(os_path.isdir(album_dir_path), f'album_dir_path does not exist: {album_dir_path!r}')
    album_config['album_dir_path'] = album_dir_path

    if not album_config['title']:
        album_config['title'] = os_path.basename(album_dir_path)

    if not album_config['cover_file']:
        album_config['cover_file'] = None
    else:
        album_config['cover_file'] = utils.get_abs_joined_path(album_dir_path, album_config['cover_file'])
        utils.assert_(utils.is_sub_path(album_config['cover_file'], album_dir_path), f'cover_file must be within album_dir_path: {album_config["cover_file"]!r}')
        utils.assert_(os_path.isfile(album_config['cover_file']), f'cover_file does not exist: {album_config["cover_file"]!r}')

    if not album_config['output_filename']:
        album_config['output_filename'] = 'player.html'

    if not is_abs_path:
        album_config['album_dir_path'] = utils.get_rel_path(album_config['album_dir_path'], base_dir_path)
        if album_config['cover_file']:
            album_config['cover_file'] = utils.get_rel_path(album_config['cover_file'], album_dir_path)

    return album_config


def generate(album_config: dict, *, base_dir_path: str = '.', overwrite: bool = False) -> None:
    album_config = normalize_album_config(album_config, base_dir_path=base_dir_path)

    logger.info('Generating player in: %r', album_config['album_dir_path'])

    music_info_groups = get_music_groups(album_config['album_dir_path'], album_config['recursively'], album_config['sort_type'])
    music_info_list = [music_info for group in music_info_groups for music_info in group['music_info_sub_list']]
    logger.info('Found %d groups, %d files', len(music_info_groups), len(music_info_list))
    logger.debug('music_info_groups: %s', json.dumps(music_info_groups, indent=4, ensure_ascii=False))
    logger.debug('music_info_list: %s', json.dumps(music_info_list, indent=4, ensure_ascii=False))

    lang = utils.detect_language(' '.join([album_config['title']] + [_['name'] for _ in music_info_list]))

    # Get same result for same dir name, which may sync between computers
    storage_key_prefix = f'music_{get_hash(os_path.basename(album_config["album_dir_path"]))}_'

    env = utils.get_jinja_env()
    template = env.get_template('player.html')
    result = template.render(
        lang=lang,
        title=album_config['title'],
        cover_file=utils.get_rel_path(album_config['cover_file'], album_config['album_dir_path']) if album_config['cover_file'] else None,
        music_info_groups=music_info_groups,
        music_info_list=music_info_list,
        storage_key_prefix=storage_key_prefix,
    )

    output_file_path = os_path.join(album_config['album_dir_path'], album_config['output_filename'])
    if os_path.exists(output_file_path) and not overwrite:
        raise FileExistsError(f'Output file already exists: {output_file_path!r}, use -f/--force to overwrite')

    logger.info('Writing to file: %r', output_file_path)
    with open(output_file_path, 'w', encoding='UTF-8') as f:
        f.write(result)
