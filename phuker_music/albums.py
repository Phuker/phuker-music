#!/usr/bin/env python3
# encoding: utf-8

import os
import logging
import json

from . import utils
from .utils import os_path
from . import player


logger: logging.Logger = logging.getLogger(__name__)


def normalize_albums_config(albums_config: dict, *, albums_config_dir_path: str, check_exists: bool = True, absolute: bool = True) -> dict:
    utils.assert_(isinstance(albums_config, dict), 'invalid albums_config')
    utils.assert_(isinstance(albums_config.get('albums_dir_path'), str) and albums_config['albums_dir_path'], 'invalid albums_dir_path')
    utils.assert_(isinstance(albums_config.get('albums_index_filename'), str) and albums_config['albums_index_filename'], 'invalid albums_index_filename')
    utils.assert_('/' not in albums_config['albums_index_filename'] and '\\' not in albums_config['albums_index_filename'], f'albums_index_filename must not contain path separators: {albums_config["albums_index_filename"]!r}')
    utils.assert_(isinstance(albums_config.get('albums_title'), str) and albums_config['albums_title'], 'invalid albums_title')
    utils.assert_(isinstance(albums_config.get('albums'), list), 'invalid albums')

    albums_dir_path = utils.get_abs_joined_path(albums_config_dir_path, albums_config['albums_dir_path'])
    utils.assert_(not check_exists or os_path.isdir(albums_dir_path), f'albums_dir_path does not exist: {albums_dir_path!r}')
    albums_config['albums_dir_path'] = albums_dir_path

    for i, album_config_input in enumerate(albums_config['albums']):
        albums_config['albums'][i] = player.normalize_album_config(album_config_input, base_dir_path=albums_dir_path, check_exists=check_exists, absolute=absolute)
        utils.assert_(
            utils.is_sub_path(utils.get_abs_joined_path(albums_dir_path, albums_config['albums'][i]['album_dir_path']), albums_dir_path),
            f'album_dir_path must be within albums_dir_path: {albums_config["albums"][i]["album_dir_path"]!r}',
        )

    if not absolute:
        albums_config['albums_dir_path'] = utils.get_rel_path(albums_config['albums_dir_path'], albums_config_dir_path)

    return albums_config


def get_config(albums_config_file_path: str, *, check_exists: bool = True, absolute: bool = True) -> dict[str, object]:
    with open(albums_config_file_path, 'r', encoding='UTF-8') as f:
        albums_config = json.load(f)

    albums_config_dir_path = os_path.dirname(albums_config_file_path)
    albums_config = normalize_albums_config(albums_config, albums_config_dir_path=albums_config_dir_path, check_exists=check_exists, absolute=absolute)

    return albums_config


def main(albums_config_file_path: str, overwrite: bool = False) -> None:
    albums_config_file_path = utils.get_abs_joined_path(albums_config_file_path)
    utils.assert_(os_path.isfile(albums_config_file_path), f'Albums config file does not exist: {albums_config_file_path!r}')

    logger.info('Loading albums config file: %r', albums_config_file_path)
    albums_config = get_config(albums_config_file_path)
    logger.debug('Albums config: %s', json.dumps(albums_config, indent=4, ensure_ascii=False))
    logger.info('Found %d albums', len(albums_config['albums']))

    albums_dir_path = albums_config['albums_dir_path']
    albums_index_file_path = os_path.join(albums_dir_path, albums_config['albums_index_filename'])

    if os_path.exists(albums_index_file_path) and not overwrite:
        raise FileExistsError(f'Index page file already exists: {albums_index_file_path!r}, use -f/--force to overwrite')

    indexes = []
    for i, album_config in enumerate(albums_config['albums']):
        logger.info('(%d/%d) Album dir path: %r', i + 1, len(albums_config['albums']), album_config['album_dir_path'])
        player.generate(album_config, base_dir_path=albums_dir_path, overwrite=overwrite)

        player_path = utils.get_rel_path(os_path.join(album_config['album_dir_path'], album_config['player_filename']), albums_dir_path)
        cover_path = utils.get_rel_path(os_path.join(album_config['album_dir_path'], album_config['cover_file']), albums_dir_path) if album_config['cover_file'] else None

        indexes.append((
            player_path,
            album_config['title'],
            cover_path,
        ))

    lang = utils.detect_language(' '.join([albums_config['albums_title']] + [title for _, title, _ in indexes]))
    manifest_url = utils.get_web_app_manifest_data_url(albums_index_file_path)

    logger.info('Generating index page: %r', albums_index_file_path)
    env = utils.get_jinja_env()
    template = env.get_template('albums.html')
    result = template.render(lang=lang, manifest_url=manifest_url, albums_title=albums_config['albums_title'], indexes=indexes)

    logger.info('Writing index page: %r', albums_index_file_path)
    with open(albums_index_file_path, 'w', encoding='UTF-8') as f:
        f.write(result)
