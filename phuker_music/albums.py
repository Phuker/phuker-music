#!/usr/bin/env python3
# encoding: utf-8

import os
import logging
import json

from . import _utils
from . import player


logger: logging.Logger = logging.getLogger(__name__)


def get_config(file_path: str) -> dict[str, object]:
    with open(file_path, 'r', encoding='UTF-8') as f:
        config = json.load(f)

    config_dir_path = os.path.dirname(file_path)

    albums_index_file_path = config['albums_index_file_path']
    albums_index_file_path = os.path.abspath(os.path.join(config_dir_path, os.path.expanduser(albums_index_file_path)))
    _utils._assert(os.path.isdir(os.path.dirname(albums_index_file_path)), f'Invalid albums_index_file_path, whose dir not exist: {albums_index_file_path!r}')
    config['albums_index_file_path'] = albums_index_file_path

    for i, _album_config in enumerate(config['albums']):
        album_config = {
            'dir_path': None,
            'title': None,
            'cover_file': None,
            'recursively': False,
            'sort_type': 'filename',
            'overwrite': True,
            'output_filename': 'player.html',
        }
        album_config.update(_album_config)

        _utils._assert(isinstance(album_config['dir_path'], str), f"invalid config['albums'][{i}]['dir_path']")
        _utils._assert(isinstance(album_config['title'], (str, type(None))), f"invalid config['albums'][{i}]['title']")
        _utils._assert(isinstance(album_config['cover_file'], (str, type(None))), f"invalid config['albums'][{i}]['cover_file']")
        _utils._assert(isinstance(album_config['recursively'], bool), f"invalid config['albums'][{i}]['recursively']")
        _utils._assert(isinstance(album_config['sort_type'], str), f"invalid config['albums'][{i}]['sort_type']")
        _utils._assert(isinstance(album_config['overwrite'], bool), f"invalid config['albums'][{i}]['overwrite']")
        _utils._assert(isinstance(album_config['output_filename'], str), f"invalid config['albums'][{i}]['output_filename']")

        dir_path = album_config['dir_path']
        dir_path = os.path.abspath(os.path.join(config_dir_path, os.path.expanduser(dir_path)))
        _utils._assert(os.path.isdir(dir_path), f'Album dir path not exist: {dir_path!r}')
        album_config['dir_path'] = dir_path

        if not album_config['title']:
            album_config['title'] = os.path.basename(dir_path)

        config['albums'][i] = album_config

    return config


def main(config_file: str, force: bool = False) -> None:
    logger.info('Load config file: %r', config_file)
    config = get_config(config_file)
    logger.debug('Config: %s', json.dumps(config, indent=4, ensure_ascii=False))
    logger.info('Got %d albums', len(config['albums']))

    if os.path.exists(config['albums_index_file_path']) and not force:
        raise FileExistsError(f'Output file already exists: {config["albums_index_file_path"]!r}, use -f/--force to overwrite')

    indexes = []
    for i, album_config in enumerate(config['albums']):
        logger.info('(%d/%d) Album dir path: %r', i + 1, len(config['albums']), album_config['dir_path'])
        player.generate(**album_config)

        get_rel_path = lambda _path: './' + os.path.relpath(os.path.join(album_config['dir_path'], _path), os.path.dirname(config['albums_index_file_path'])).replace(os.sep, '/')
        player_path = get_rel_path(album_config['output_filename'])
        cover_path = get_rel_path(album_config['cover_file']) if album_config['cover_file'] else None

        indexes.append((
            player_path,
            album_config['title'],
            cover_path,
        ))

    lang = _utils.detect_language(' '.join(title for _, title, _ in indexes))

    logger.info('Generate index page: %r', config['albums_index_file_path'])
    env = _utils.get_jinja_env()
    template = env.get_template('albums.html')
    result = template.render(lang=lang, indexes=indexes)

    logger.info('Write index page: %r', config['albums_index_file_path'])
    with open(config['albums_index_file_path'], 'w', encoding='UTF-8') as f:
        f.write(result)
