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
albums_config_dir_path: str = ''
albums_dir_path: str = ''

scan_lock = threading.Lock()
scan_thread = None
scan_status = {
    'status': 'idle', # 'idle' 'running' 'done' 'error'
    'scanned_dirs': 0,
    'available_albums': None,
    'message': None,
}

generate_lock = threading.Lock()
generate_thread = None
generate_status = {
    'status': 'idle', # 'idle' 'running' 'done' 'error'
    'message': None,
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

        with scan_lock:
            scan_status['scanned_dirs'] += 1

        return has_audio, image_file_path_list

    try:
        _scan(albums_dir_path)

        with scan_lock:
            scan_status['status'] = 'done'
            scan_status['available_albums'] = available_albums
    except Exception as e:
        logger.exception('/api/scan failed')
        with scan_lock:
            scan_status['status'] = 'error'
            scan_status['message'] = repr(e)


@app.route('/api/scan', methods=['POST'])
def api_scan():
    global scan_thread

    def _reset_scan_status(status):
        scan_status['status'] = status
        scan_status['scanned_dirs'] = 0
        scan_status['available_albums'] = None
        scan_status['message'] = None

    with scan_lock:
        if scan_status['status'] == 'idle':
            _reset_scan_status('running')
            scan_thread = threading.Thread(target=background_scan, daemon=True)
            scan_thread.start()

            return jsonify({
                'status': 'running',
                'data': {
                    'scanned_dirs': 0,
                },
            })
        elif scan_status['status'] == 'running':
            return jsonify({
                'status': 'running',
                'data': {
                    'scanned_dirs': scan_status['scanned_dirs'],
                },
            })
        elif scan_status['status'] == 'done':
            scanned_dirs = scan_status['scanned_dirs']
            available_albums = scan_status['available_albums']
            _reset_scan_status('idle')

            if os_path.isfile(albums_config_file_path):
                albums_config = albums.get_config(albums_config_file_path, check_exists=False, absolute=False)

                # Handle mismatched albums_dir_path values between the CLI and the existing config
                # Override the albums_dir_path field in the existing config with the authoritative CLI value
                albums_config['albums_dir_path'] = utils.get_rel_path(albums_dir_path, albums_config_dir_path)
            else:
                albums_config = {
                    'albums_dir_path': utils.get_rel_path(albums_dir_path, albums_config_dir_path),
                    'albums_index_filename': constants.DEFAULT_ALBUMS_INDEX_FILENAME,
                    'albums': [],
                }

            return jsonify({
                'status': 'done',
                'data': {
                    'scanned_dirs': scanned_dirs,
                    'albums_config': albums_config,
                    'available_albums': available_albums,
                },
            })
        else:
            message = scan_status['message']
            _reset_scan_status('idle')
            return jsonify({'status': 'error', 'message': message}), 500


@app.route('/api/save-config', methods=['POST'])
def api_save_config():
    try:
        albums_config = request.get_json()
        albums_config = albums.normalize_albums_config(albums_config, albums_config_dir_path=albums_config_dir_path, absolute=False)

        with open(albums_config_file_path, 'w', encoding='UTF-8') as f:
            json.dump(albums_config, f, indent=4, ensure_ascii=False)
            f.write('\n')

        return jsonify({'status': 'done'})
    except Exception as e:
        logger.exception('/api/save-config failed')
        return jsonify({'status': 'error', 'message': repr(e)}), 500


def background_generate() -> None:
    try:
        albums.main(albums_config_file_path, overwrite=True)
        with generate_lock:
            generate_status['status'] = 'done'
    except Exception as e:
        logger.exception('/api/generate failed')
        with generate_lock:
            generate_status['status'] = 'error'
            generate_status['message'] = repr(e)


@app.route('/api/generate', methods=['POST'])
def api_generate():
    global generate_thread

    def _reset_generate_status(status):
        generate_status['status'] = status
        generate_status['message'] = None

    with generate_lock:
        if generate_status['status'] == 'idle':
            _reset_generate_status('running')
            generate_thread = threading.Thread(target=background_generate, daemon=True)
            generate_thread.start()

            return jsonify({'status': 'running'})
        elif generate_status['status'] == 'running':
            return jsonify({'status': 'running'})
        elif generate_status['status'] == 'done':
            _reset_generate_status('idle')
            return jsonify({'status': 'done'})
        else:
            message = generate_status['message']
            _reset_generate_status('idle')
            return jsonify({'status': 'error', 'message': message}), 500


@app.route('/')
def index():
    return send_from_directory('static', 'albums_webui.html')


def main(_albums_config_file_path: str, _albums_dir_path: str, host: str, port: int, *, trusted_hosts: list[str]) -> None:
    global albums_config_file_path, albums_config_dir_path, albums_dir_path

    albums_config_file_path = utils.get_abs_joined_path(_albums_config_file_path)
    albums_config_dir_path = os_path.dirname(albums_config_file_path)
    logger.info('Albums config file: %r', albums_config_file_path)

    albums_dir_path = utils.get_abs_joined_path(_albums_dir_path)
    utils.assert_(os_path.isdir(albums_dir_path), f'Albums directory does not exist: {albums_dir_path!r}')
    logger.info('Albums directory: %r', albums_dir_path)

    logger.debug('Flask TRUSTED_HOSTS config: %r', trusted_hosts)
    app.config['TRUSTED_HOSTS'] = trusted_hosts

    logger.info('Albums WebUI listening on %s:%d, open http://127.0.0.1:%d/ in browser to view', host, port, port)
    app.run(host=host, port=port, debug=False, threaded=True)
