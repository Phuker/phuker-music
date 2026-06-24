#!/usr/bin/env python3
# encoding: utf-8

import sys
import argparse
import logging

from . import __version__
from . import constants
from . import utils
from . import player
from . import albums
from . import albums_webui


logger: logging.Logger = logging.getLogger(__name__)


def _help_formatter(prog: str) -> argparse.HelpFormatter:
    return argparse.HelpFormatter(prog, max_help_position=50, width=500)


def _player_command(shell_args: argparse.Namespace) -> None:
    album_config = {
        'album_dir_path': shell_args.album_dir_path,
        'title': shell_args.title,
        'cover_file': shell_args.cover,
        'player_filename': shell_args.player_filename,
        'recursively': shell_args.recursively,
        'sort_type': shell_args.sort_type,
    }
    player.generate(album_config, overwrite=shell_args.force)


def _albums_command(shell_args: argparse.Namespace) -> None:
    albums.main(shell_args.albums_config_file_path, overwrite=shell_args.force)


def _albums_webui_command(shell_args: argparse.Namespace) -> None:
    albums_webui.main(shell_args.albums_config_file_path, shell_args.albums_dir_path, shell_args.host, shell_args.port, trusted_hosts=shell_args.trusted_hosts)


def _add_player_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser_player = subparsers.add_parser(
        'player',
        help='Generate music player HTML for a single album',
        description='Generate music player HTML for a single album',
        formatter_class=_help_formatter,
    )

    parser_player.add_argument('album_dir_path', metavar='dir_path', help='Path to the album directory')
    parser_player.add_argument('-t', '--title', metavar='title', help='Album title, default: directory name')
    parser_player.add_argument('-c', '--cover', metavar='file', help='Album cover file path, relative to dir_path')
    parser_player.add_argument('--player-filename', metavar='filename', default=constants.DEFAULT_PLAYER_FILENAME, help='Player filename, default: %(default)s')
    parser_player.add_argument('-r', '--recursively', action='store_true', help='Recursively scan subdirectories for audio files')
    parser_player.add_argument('--sort-type', metavar='type', choices=constants.CHOICES_SORT_TYPE, default=constants.DEFAULT_SORT_TYPE, help='Sort type, choices: %(choices)s, default: %(default)s')
    parser_player.add_argument('-f', '--force', action='store_true', help='Overwrite player file if it exists')
    parser_player.add_argument('-v', '--verbose', action='count', default=0, dest='sub_verbose', help='Increase verbosity level')

    parser_player.set_defaults(func=_player_command)


def _add_albums_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser_albums = subparsers.add_parser(
        'albums',
        help='Generate player and index HTML for multiple albums',
        description='Generate player and index HTML for multiple albums',
        formatter_class=_help_formatter,
    )

    parser_albums.add_argument('albums_config_file_path', metavar='config_file', help='Albums config file path')
    parser_albums.add_argument('-f', '--force', action='store_true', help='Overwrite index page and player files if they exist')
    parser_albums.add_argument('-v', '--verbose', action='count', default=0, dest='sub_verbose', help='Increase verbosity level')

    parser_albums.set_defaults(func=_albums_command)


def _add_albums_webui_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser_webui = subparsers.add_parser(
        'albums-webui',
        help='Launch a web UI to edit the albums config and generate player and index HTML for multiple albums',
        description='Launch a web UI to edit the albums config and generate player and index HTML for multiple albums',
        formatter_class=_help_formatter,
    )

    parser_webui.add_argument('albums_config_file_path', metavar='config_file', help='Albums config file path')
    parser_webui.add_argument('albums_dir_path', metavar='dir_path', help='Albums directory path')
    parser_webui.add_argument('--host', metavar='host', default=constants.DEFAULT_WEBUI_HOST, help='Host to bind to, default: %(default)s')
    parser_webui.add_argument('--port', metavar='port', type=int, default=constants.DEFAULT_WEBUI_PORT, help='Port to bind to, default: %(default)s')
    parser_webui.add_argument('--trusted-host', metavar='host', dest='trusted_hosts', action='append', default=constants.DEFAULT_WEBUI_TRUSTED_HOSTS, help='Add a trusted request hostname, can be specified multiple times, default: %(default)s')
    parser_webui.add_argument('-v', '--verbose', action='count', default=0, dest='sub_verbose', help='Increase verbosity level')

    parser_webui.set_defaults(func=_albums_webui_command)


def _setup_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='phuker-music',
        description='Music player HTML generator',
        formatter_class=_help_formatter,
    )

    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity level')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}', help='Show version and exit')

    subparsers = parser.add_subparsers(dest='command', metavar='command', required=True)
    _add_player_subparser(subparsers)
    _add_albums_subparser(subparsers)
    _add_albums_webui_subparser(subparsers)

    return parser


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    utils.init_logging(logging_format='\x1b[1m%(asctime)s [%(module)s][%(levelname)s]:\x1b[0m%(message)s')

    parser = _setup_args()
    shell_args = parser.parse_args(argv)
    shell_args.verbose += shell_args.sub_verbose
    if shell_args.verbose >= 1:
        logging.root.setLevel(logging.DEBUG)

    logger.debug('Command line arguments: %r', shell_args)

    shell_args.func(shell_args)


if __name__ == '__main__':
    main()
