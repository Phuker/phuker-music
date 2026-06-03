#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
import logging
import atexit
import json
import base64

import jinja2

from . import __version__


logger = logging.getLogger(__name__)
lang_identifier = None


def _assert(expr, msg=''):
    if not expr:
        raise AssertionError(msg)


def _init_logging(logging_format):
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

    # Buggy when all caps text
    lang, prob = lang_identifier.classify(text.lower())
    if prob > 0.98:
        return lang
    else:
        return 'en'


def get_jinja_env():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    def global_read_file(relative_file_path):
        file_path = os.path.join(script_dir, 'templates', relative_file_path)

        with open(file_path, 'r', encoding='UTF-8') as f:
            return f.read()

    def global_read_file_as_data_url(relative_file_path, mime):
        file_path = os.path.join(script_dir, 'templates', relative_file_path)

        with open(file_path, 'rb') as f:
            content = f.read()
            base64_content = base64.b64encode(content).decode()

        return f'data:{mime};base64,{base64_content}'

    def filter_json_encode(obj):
        result = json.dumps(obj, indent=4)

        # Like PHP JSON_HEX_TAG, prevent XSS
        # https://www.php.net/manual/en/json.constants.php
        result = result.replace('<', '\\u003c').replace('>', '\\u003e')

        return result

    loader = jinja2.FileSystemLoader(os.path.join(script_dir, 'templates'))
    env = jinja2.Environment(loader=loader, autoescape=True)

    env.globals['version'] = __version__
    env.globals['read_file'] = global_read_file
    env.globals['read_file_as_data_url'] = global_read_file_as_data_url
    env.filters['json_encode'] = filter_json_encode

    return env
