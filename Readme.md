# phuker-music

[Demo](https://phuker.github.io/phuker-music/) | [GitHub](https://github.com/Phuker/phuker-music) | [PyPI](https://pypi.org/project/phuker-music/) | Readme (English, [简体中文](https://github.com/Phuker/phuker-music/blob/main/Readme.zh-CN.md))

Yet another HTML music player generator. Scan a directory of audio files and generate an offline, all-in-one single HTML player file. Also generates player pages for multiple albums plus an index page via a JSON config.

You can try the [demo](https://phuker.github.io/phuker-music/) to see what the generated index page and players look like. Grant system notification permission to display a notification when each track starts playing.

## Features

- No loan ads or subscription popups
- No AI
- No tracking, analytics, statistics, or telemetry
- No user data uploads
- No extra assets — No JS/CSS dependencies, no web fonts, no CDN
- **Only a fucking single HTML file**

## Install and run

### Run with uvx (without installation)

```bash
uvx phuker-music --help
```

### Run with pipx (without installation)

```bash
pipx run phuker-music --help
```

### Install with uv and run

```bash
uv tool install phuker-music
phuker-music --help
```

### Install with pipx and run

```bash
pipx install phuker-music
phuker-music --help
```

### Install with pip and run

```bash
pip install phuker-music
phuker-music --help
```

## Quick start

### Generate music player HTML for a single album

First, `cd` to a directory that contains audio files, for example one cover image and three audio files:

```text
.
|-- Cafe ambience.m4a
|-- Cover.jpg
|-- Crowd Talking Quietly Stadium.mp3
`-- Distant train with cicadas.m4a
```

Then run:

```bash
phuker-music player --force --cover Cover.jpg .
```

You will get:

```text
.
|-- Cafe ambience.m4a
|-- Cover.jpg
|-- Crowd Talking Quietly Stadium.mp3
|-- Distant train with cicadas.m4a
`-- player.html                        <-- player HTML file
```

Open `player.html` in a browser to use the player.

### Generate player and index page for multiple albums

`cd` to a directory containing multiple album directories, for example two album directories:

```text
.
|-- Ambience
|   |-- Cafe ambience.m4a
|   |-- Cover.jpg
|   |-- Crowd Talking Quietly Stadium.mp3
|   `-- Distant train with cicadas.m4a
`-- Nature
    |-- Cover.jpg
    |-- FL Mocking birds.mp3
    |-- Frogs and nature in Southern Brasil in August.m4a
    |-- Morning birds.m4a
    |-- Nature.m4a
    |-- Rain.ogg
    `-- Thunder.mp3
```

Then run:

```bash
phuker-music albums-webui ./albums.json
```

Visit <http://127.0.0.1:8000/> in a browser, drag albums from the Available column to the Albums column, click the `Save & Generate` button at the top, and you will get:

```text
.
|-- albums.json                                            <-- config file
|-- Ambience
|   |-- Cafe ambience.m4a
|   |-- Cover.jpg
|   |-- Crowd Talking Quietly Stadium.mp3
|   |-- Distant train with cicadas.m4a
|   `-- player.html                                        <-- player HTML file
|-- index.html                                             <-- index HTML file
`-- Nature
    |-- Cover.jpg
    |-- FL Mocking birds.mp3
    |-- Frogs and nature in Southern Brasil in August.m4a
    |-- Morning birds.m4a
    |-- Nature.m4a
    |-- player.html                                        <-- player HTML file
    |-- Rain.ogg
    `-- Thunder.mp3
```

Open `index.html` in a browser to view the index page.

## Usage

```console
$ phuker-music --help
usage: phuker-music [-h] [-v] [-V] command ...

Music player HTML generator

positional arguments:
  command
    player        Generate music player HTML for a single album
    albums        Generate player and index HTML for multiple albums
    albums-webui  Launch a web UI to edit albums config and generate player and index HTML for multiple albums

options:
  -h, --help      show this help message and exit
  -v, --verbose   Increase verbosity level
  -V, --version   Show version and exit
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

Generate player and index HTML for multiple albums

positional arguments:
  config_file    Albums config file path

options:
  -h, --help     show this help message and exit
  -f, --force    Overwrite output file if it exists
  -v, --verbose  Increase verbosity level
```

```console
$ phuker-music albums-webui --help
usage: phuker-music albums-webui [-h] [--host HOST] [--port PORT] [-v] config_file

Launch a web UI to edit albums config and generate player and index HTML for multiple albums

positional arguments:
  config_file    Albums config file path

options:
  -h, --help     show this help message and exit
  --host HOST    Host to bind to, default: 127.0.0.1
  --port PORT    Port to bind to, default: 8000
  -v, --verbose  Increase verbosity level
```

## License

MIT
