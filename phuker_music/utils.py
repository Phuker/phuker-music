#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
import logging
import atexit
import functools
import json
import base64

import jinja2

from . import __version__


logger: logging.Logger = logging.getLogger(__name__)
lang_identifier: object | None = None


def assert_(expr: object, msg: str = '') -> None:
    if not expr:
        raise AssertionError(msg)


def init_logging(logging_format: str) -> None:
    logging_stream = sys.stdout
    logging_level = logging.INFO

    if logging_stream.isatty():
        logging_date_format = '%H:%M:%S'
        atexit.register(lambda: logger.info('Exiting'))
    else:
        logging_date_format = '%Y-%m-%d %H:%M:%S'
        atexit.register(lambda: logger.info('Exiting\n'))

    logging.basicConfig(
        level=logging_level,
        format=logging_format,
        datefmt=logging_date_format,
        stream=logging_stream,
    )

    logging.addLevelName(logging.CRITICAL, f'\x1b[31m{logging.getLevelName(logging.CRITICAL)}\x1b[39m')
    logging.addLevelName(logging.ERROR, f'\x1b[31m{logging.getLevelName(logging.ERROR)}\x1b[39m')
    logging.addLevelName(logging.WARNING, f'\x1b[33m{logging.getLevelName(logging.WARNING)}\x1b[39m')
    logging.addLevelName(logging.INFO, f'\x1b[36m{logging.getLevelName(logging.INFO)}\x1b[39m')
    logging.addLevelName(logging.DEBUG, f'\x1b[36m{logging.getLevelName(logging.DEBUG)}\x1b[39m')


class OsPathProxy:
    # Proxy os.path on Windows: replace \ with / in str return values of wrapped functions

    _WRAPPED_FUNCS = {
        'abspath',
        'commonpath',
        'dirname',
        'expanduser',
        'join',
        'normpath',
        'realpath',
        'relpath',
    }

    def __init__(self):
        pass

    def __getattr__(self, name):
        obj = getattr(os.path, name)

        if name not in self._WRAPPED_FUNCS:
            return obj
        else:
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                return_val = obj(*args, **kwargs)
                if isinstance(return_val, str):
                    return return_val.replace(os.sep, '/')
                else:
                    return return_val

            return wrapper


if os.name == 'nt':
    os_path = OsPathProxy()
else:
    os_path = os.path


def match_ext_list(file_path: str, ext_list: tuple[str, ...]) -> bool:
    return os_path.splitext(file_path)[1].lower() in ext_list


def is_sub_path(path: str, parent_path: str) -> bool:
    path = os_path.abspath(os_path.expanduser(path))
    parent_path = os_path.abspath(os_path.expanduser(parent_path))

    return parent_path == os_path.commonpath([path, parent_path])


def get_rel_path(path: str, start_dir_path: str) -> str:
    path = os_path.expanduser(path)
    start_dir_path = os_path.expanduser(start_dir_path)

    result = os_path.relpath(path, start_dir_path)
    if result in ('.', '..') or result.startswith('../'):
        return result
    else:
        return './' + result


def get_abs_joined_path(*paths: str) -> str:
    assert_(len(paths) >= 1, f'paths must have at least 1 element, got: {paths!r}')
    for path in paths:
        assert_(isinstance(path, str) and path, f'path must be non-empty str: {path!r}')

    expanded = tuple(os_path.expanduser(path) for path in paths)

    return os_path.abspath(os_path.join(*expanded))


STATIC_DIR_PATH: str = os_path.join(os_path.dirname(os_path.abspath(__file__)), 'static')


def read_static_file_as_text(relative_file_path: str) -> str:
    file_path = os_path.join(STATIC_DIR_PATH, relative_file_path)

    with open(file_path, 'r', encoding='UTF-8') as f:
        return f.read()


def read_static_file_as_data_url(relative_file_path: str, mime: str) -> str:
    file_path = os_path.join(STATIC_DIR_PATH, relative_file_path)

    with open(file_path, 'rb') as f:
        content = f.read()
        base64_content = base64.b64encode(content).decode()

    return f'data:{mime};base64,{base64_content}'


def get_web_app_manifest_data_url(title: str, filename: str) -> str:
    manifest = {
        'short_name': title,
        'name': title,
        'start_url': f'./{filename}',
        'display': 'minimal-ui',
        'icons': [
            {
                'type': 'image/png',
                'sizes': '512x512',
                'src': read_static_file_as_data_url('images/album-512.png', 'image/png'),
            },
            {
                'type': 'image/png',
                'sizes': '192x192',
                'src': read_static_file_as_data_url('images/album-192.png', 'image/png'),
            },
        ],
    }

    manifest_json = json.dumps(manifest, separators=(',', ':'), ensure_ascii=False)
    manifest_base64 = base64.b64encode(manifest_json.encode()).decode()

    return f'data:application/manifest+json;base64,{manifest_base64}'


def safe_json_encode(obj: object) -> str:
    result = json.dumps(obj, indent=4, ensure_ascii=False)

    # Like PHP JSON_HEX_TAG, prevent XSS
    # https://www.php.net/manual/en/json.constants.php
    result = result.replace('<', '\\u003c').replace('>', '\\u003e')

    return result


def get_jinja_env() -> jinja2.Environment:
    templates_dir_path = os_path.join(os_path.dirname(os_path.abspath(__file__)), 'templates')
    loader = jinja2.FileSystemLoader(templates_dir_path)
    env = jinja2.Environment(loader=loader, autoescape=True, keep_trailing_newline=True)

    env.globals['version'] = __version__
    env.globals['read_static_file_as_text'] = read_static_file_as_text
    env.globals['read_static_file_as_data_url'] = read_static_file_as_data_url
    env.filters['safe_json_encode'] = safe_json_encode

    return env


def detect_language(text: str) -> str:
    global lang_identifier

    # Lazy init
    # subsequent calls reuse the instance for performance
    if lang_identifier is None:
        import langid

        lang_identifier = langid.langid.LanguageIdentifier.from_modelstring(langid.langid.model, norm_probs=True)
        lang_identifier.set_languages([_ for _ in lang_identifier.nb_classes if _ not in (
            'la', # Sometimes incorrectly returns Latin
        )])

    # Return value examples:
    # '' -> ('en', 0.16953482986139237)
    # 'Knowledge is power.' -> ('en', 0.9998478611629795)
    # Buggy when all caps text
    lang, prob = lang_identifier.classify(text.lower())
    if prob > 0.98:
        return lang
    else:
        return 'en'
