# phuker-music

[Demo](https://phuker.github.io/phuker-music/) | [GitHub](https://github.com/Phuker/phuker-music) | [PyPI](https://pypi.org/project/phuker-music/) | Readme (English, [简体中文](https://github.com/Phuker/phuker-music/blob/main/Readme.zh-CN.md))

Yet another HTML music player generator. Scan a directory of audio files and generate an offline, all-in-one single HTML player file. Also generates player pages for multiple albums plus an index page via a JSON config.

You can try the [demo](https://phuker.github.io/phuker-music/) to see what generated index page and players look like. Grant system notifications permission to display a notification when each track starts playing.

## Features

- No loan ads or subscription popups
- No AI
- No tracking, analytics, statistics, or telemetry
- No user data uploads
- No extra assets — No JS/CSS dependencies, no web fonts, no CDN
- **Only a fucking single HTML file**

## Quick Start

First, `cd` to a directory that contains audio files, then:

### Run with uvx

```bash
uvx phuker-music player .
```

### Run with pipx

```bash
pipx run phuker-music player .
```

### Install with uv and run

```bash
uv tool install phuker-music
phuker-music player .
```

### Install with pipx and run

```bash
pipx install phuker-music
phuker-music player .
```

### Install with pip and run

```bash
pip install phuker-music
phuker-music player .
```

## Usage

```console
$ phuker-music --help
usage: phuker-music [-h] [-v] [-V] command ...

Music player HTML generator

positional arguments:
  command
    player       Generate music player HTML for a single album
    albums       Generate player and index page for all albums

options:
  -h, --help     show this help message and exit
  -v, --verbose  Increase verbosity level
  -V, --version  Show version and exit
```

```console
$ phuker-music player --help
usage: phuker-music player [-h] [-t title] [-c file] [-o filename] [-r] [--sort-type type] [-f] [-v] dir_path

Generate music player HTML for a single album

positional arguments:
  dir_path                        Path to the album directory

options:
  -h, --help                      show this help message and exit
  -t, --title title               Album title, default: directory name
  -c, --cover file                Album cover file path, relative to dir_path
  -o, --output-filename filename  Output filename, default: player.html
  -r, --recursively               Recursively scan subdirectories for audio files
  --sort-type type                Sort type, default: filename, choices: filename, mtime_desc
  -f, --force                     Overwrite output file if it exists
  -v, --verbose                   Increase verbosity level
```

```console
$ phuker-music albums --help
usage: phuker-music albums [-h] [-f] [-v] config_file

Generate player and index page for all albums

positional arguments:
  config_file    Config file path

options:
  -h, --help     show this help message and exit
  -f, --force    Overwrite output file if it exists
  -v, --verbose  Increase verbosity level
```

## License

MIT
