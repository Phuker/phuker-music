#!/usr/bin/env python3
# encoding: utf-8

import os
import json
import threading
import logging

from flask import Flask, request, jsonify, send_from_directory

from . import constants
from . import utils
from .utils import os_path
from . import albums


logger: logging.Logger = logging.getLogger(__name__)

app = Flask(__name__)

albums_config_file_path: str = ''
albums_dir_path: str = ''

scan_lock = threading.Lock()
scan_status = {
    'status': 'idle', # 'idle' 'scanning' 'done' 'error'
    'scanned_dirs': 0,
    'available_albums': None,
}


def background_scan() -> None:
    available_albums = {}

    def _scan(root: str) -> tuple[bool, list]:
        logger.info('Scan dir: %r', root)
        root, dirs, files = next(os.walk(root))
        root = root.replace(os.sep, '/')

        has_audio = any(utils.match_ext_list(file, constants.AUDIO_EXT_LIST) for file in files)
        image_file_path_list = [os_path.join(root, file) for file in files if utils.match_ext_list(file, constants.IMAGE_EXT_LIST)]

        for dir_name in dirs:
            sub_root = os_path.join(root, dir_name)
            sub_has_audio, sub_image_file_path_list = _scan(sub_root)
            has_audio = has_audio or sub_has_audio
            image_file_path_list += sub_image_file_path_list

        if has_audio:
            available_albums[utils.get_rel_path(root, albums_dir_path)] = [utils.get_rel_path(_, root) for _ in sorted(image_file_path_list)]

        scan_status['scanned_dirs'] += 1

        return has_audio, image_file_path_list

    try:
        _scan(albums_dir_path)

        scan_status['available_albums'] = available_albums
        scan_status['status'] = 'done'
    except Exception:
        logger.exception('Scan failed')
        scan_status['status'] = 'error'


@app.route('/api/scan')
def api_scan():
    with scan_lock:
        if scan_status['status'] == 'idle':
            scan_status['status'] = 'scanning'
            scan_status['scanned_dirs'] = 0
            thread = threading.Thread(target=background_scan, daemon=True)
            thread.start()
            return jsonify({
                'status': 'scanning',
                'data': {
                    'scanned_dirs': 0,
                },
            })
        elif scan_status['status'] == 'scanning':
            return jsonify({
                'status': 'scanning',
                'data': {
                    'scanned_dirs': scan_status['scanned_dirs'],
                },
            })
        elif scan_status['status'] == 'done':
            if os_path.isfile(albums_config_file_path):
                albums_config = albums.get_config(albums_config_file_path, is_abs_path=False)
            else:
                albums_config = {
                    'albums_index_file_path': './index.html',
                    'albums': [],
                }

            return jsonify({
                'status': 'done',
                'data': {
                    'scanned_dirs': scan_status['scanned_dirs'],
                    'albums_config': albums_config,
                    'available_albums': scan_status['available_albums'],
                },
            })
        else:
            return jsonify({'status': 'error', 'message': 'Scan failed'}), 500


@app.route('/api/save-config', methods=['POST'])
def api_save_config():
    try:
        albums_config = request.get_json()
        albums_config = albums.normalize_albums_config(albums_config, albums_dir_path=albums_dir_path, is_abs_path=False)

        with open(albums_config_file_path, 'w', encoding='UTF-8') as f:
            json.dump(albums_config, f, indent=4, ensure_ascii=False)
            f.write('\n')

        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.exception('/api/save-config failed')
        return jsonify({'status': 'error', 'message': repr(e)}), 500


@app.route('/api/regenerate', methods=['POST'])
def api_regenerate():
    try:
        albums.main(albums_config_file_path, force=True)

        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.exception('/api/regenerate failed')
        return jsonify({'status': 'error', 'message': repr(e)}), 500


@app.route('/')
def index():
    return send_from_directory('static', 'albums_webui.html')


def main(_albums_config_file_path: str, host: str = '127.0.0.1', port: int = 8000) -> None:
    global albums_config_file_path, albums_dir_path

    albums_config_file_path = utils.get_abs_joined_path(_albums_config_file_path)
    logger.info('Albums config file: %r', albums_config_file_path)

    albums_dir_path = os_path.dirname(albums_config_file_path)
    logger.info('Albums directory: %r', albums_dir_path)

    logger.info('Albums WebUI starting at http://%s:%d/', host, port)
    app.run(host=host, port=port, debug=False, threaded=True)
