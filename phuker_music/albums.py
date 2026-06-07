#!/usr/bin/env python3
# encoding: utf-8

import os
import logging
import json

from . import utils
from . import player


logger: logging.Logger = logging.getLogger(__name__)


def normalize_album_config(album_config_input: dict, albums_dir_path: str) -> dict:
    album_config = {
        'album_dir_path': None,
        'title': None,
        'cover_file': None,
        'output_filename': 'player.html',
        'recursively': False,
        'sort_type': 'filename',
        'overwrite': True,
    }
    album_config.update(album_config_input)

    utils._assert(isinstance(album_config['album_dir_path'], str), f'invalid album_config: {album_config!r}')
    utils._assert(isinstance(album_config['title'], (str, type(None))), f'invalid album_config: {album_config!r}')
    utils._assert(isinstance(album_config['cover_file'], (str, type(None))), f'invalid album_config: {album_config!r}')
    utils._assert(isinstance(album_config['output_filename'], str), f'invalid album_config: {album_config!r}')
    utils._assert(isinstance(album_config['recursively'], bool), f'invalid album_config: {album_config!r}')
    utils._assert(isinstance(album_config['sort_type'], str), f'invalid album_config: {album_config!r}')
    utils._assert(isinstance(album_config['overwrite'], bool), f'invalid album_config: {album_config!r}')

    album_dir_path = album_config['album_dir_path']
    album_dir_path = os.path.abspath(os.path.join(albums_dir_path, os.path.expanduser(album_dir_path))).replace(os.sep, '/')
    utils._assert(utils.is_sub_path(album_dir_path, albums_dir_path), f'album_dir_path must be within albums_dir_path: {album_dir_path!r}')
    utils._assert(os.path.isdir(album_dir_path), f'Album directory does not exist: {album_dir_path!r}')
    album_config['album_dir_path'] = album_dir_path

    if not album_config['title']:
        album_config['title'] = os.path.basename(album_dir_path)

    return album_config


def normalize_albums_config(albums_config: dict, albums_dir_path: str) -> None:
    albums_index_file_path = albums_config['albums_index_file_path']
    albums_index_file_path = os.path.abspath(os.path.join(albums_dir_path, os.path.expanduser(albums_index_file_path))).replace(os.sep, '/')
    utils._assert(utils.is_sub_path(albums_index_file_path, albums_dir_path), f'albums_index_file_path must be within albums_dir_path: {albums_index_file_path!r}')
    utils._assert(os.path.isdir(os.path.dirname(albums_index_file_path)), f'Parent directory of albums_index_file_path does not exist: {albums_index_file_path!r}')
    albums_config['albums_index_file_path'] = albums_index_file_path

    for i, album_config_input in enumerate(albums_config['albums']):
        albums_config['albums'][i] = normalize_album_config(album_config_input, albums_dir_path)

    return albums_config


def get_config(albums_config_file_path: str) -> dict[str, object]:
    with open(albums_config_file_path, 'r', encoding='UTF-8') as f:
        albums_config = json.load(f)

    albums_dir_path = os.path.dirname(albums_config_file_path).replace(os.sep, '/')
    albums_config = normalize_albums_config(albums_config, albums_dir_path)

    return albums_config


def main(albums_config_file_path: str, force: bool = False) -> None:
    logger.info('Loading albums config file: %r', albums_config_file_path)
    albums_config = get_config(albums_config_file_path)
    logger.debug('Albums config: %s', json.dumps(albums_config, indent=4, ensure_ascii=False))
    logger.info('Found %d albums', len(albums_config['albums']))

    if os.path.exists(albums_config['albums_index_file_path']) and not force:
        raise FileExistsError(f'Output file already exists: {albums_config["albums_index_file_path"]!r}, use -f/--force to overwrite')

    indexes = []
    for i, album_config in enumerate(albums_config['albums']):
        logger.info('(%d/%d) Album dir path: %r', i + 1, len(albums_config['albums']), album_config['album_dir_path'])
        player.generate(**album_config)

        get_rel_path = lambda _path: './' + os.path.relpath(os.path.join(album_config['album_dir_path'], _path), os.path.dirname(albums_config['albums_index_file_path'])).replace(os.sep, '/')
        player_path = get_rel_path(album_config['output_filename'])
        cover_path = get_rel_path(album_config['cover_file']) if album_config['cover_file'] else None

        indexes.append((
            player_path,
            album_config['title'],
            cover_path,
        ))

    lang = utils.detect_language(' '.join(title for _, title, _ in indexes))

    logger.info('Generating index page: %r', albums_config['albums_index_file_path'])
    env = utils.get_jinja_env()
    template = env.get_template('albums.html')
    result = template.render(lang=lang, indexes=indexes)

    logger.info('Writing index page: %r', albums_config['albums_index_file_path'])
    with open(albums_config['albums_index_file_path'], 'w', encoding='UTF-8') as f:
        f.write(result)
