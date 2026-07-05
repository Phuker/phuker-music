# phuker-music

[Demo](https://phuker.github.io/phuker-music/) | [GitHub](https://github.com/Phuker/phuker-music) | [PyPI](https://pypi.org/project/phuker-music/) | Readme (English, [简体中文](https://github.com/Phuker/phuker-music/blob/main/Readme.zh-CN.md))

Yet another HTML music player generator. Scan a directory of audio files and generate an offline, all-in-one single HTML player file. Also generates player pages for multiple albums plus an index page via a JSON config. You can open the generated HTML files directly in a browser, sync them along with your audio files across devices, or upload them to a web server.

You can try the [demo](https://phuker.github.io/phuker-music/) to see what the generated index page and players look like.

## Typical use case

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
phuker-music albums-webui ./albums.json .
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

## Features

### The crap you won't find

- No account sign-up or paid subscription required
- No 15-second preview limit
- No splash screen ads
- No loan ads popups
- No AI
- No tracking, analytics, statistics, or telemetry
- No user data uploads
- No extra assets — No JS/CSS dependencies, no web fonts, no CDN
- **Only a fucking single HTML file**

### What it does have

- System media controls and now playing information
- System notification on track start (requires permission)
- Installable as a Progressive Web App (PWA)
- Follow system dark mode
- Background playback persistence

### What's not yet supported

- Gapless playback

## Install and run

This project requires Python 3.10 or later.

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

## Usage

```console
$ phuker-music --help
usage: phuker-music [-h] [-v] [-V] command ...

Music player HTML generator

positional arguments:
  command
    player        Generate music player HTML for a single album
    albums        Generate player and index HTML for multiple albums
    albums-webui  Launch a web UI to edit the albums config and generate player and index HTML for multiple albums

options:
  -h, --help      show this help message and exit
  -v, --verbose   Increase verbosity level
  -V, --version   Show version and exit
```

```console
$ phuker-music player --help
usage: phuker-music player [-h] [-t title] [-c file] [--player-filename filename] [-r] [--sort-type type] [-f] [-v] dir_path

Generate music player HTML for a single album

positional arguments:
  dir_path                    Path to the album directory

options:
  -h, --help                  show this help message and exit
  -t, --title title           Album title, default: directory name
  -c, --cover file            Album cover file path, relative to dir_path
  --player-filename filename  Player filename, default: player.html
  -r, --recursively           Recursively scan subdirectories for audio files
  --sort-type type            Sort type, choices: filename, mtime_desc, default: filename
  -f, --force                 Overwrite player file if it exists
  -v, --verbose               Increase verbosity level
```

```console
$ phuker-music albums --help
usage: phuker-music albums [-h] [-f] [-v] config_file

Generate player and index HTML for multiple albums

positional arguments:
  config_file    Albums config file path

options:
  -h, --help     show this help message and exit
  -f, --force    Overwrite index page and player files if they exist
  -v, --verbose  Increase verbosity level
```

```console
$ phuker-music albums-webui --help
usage: phuker-music albums-webui [-h] [--host host] [--port port] [--trusted-host host] [-v] config_file dir_path

Launch a web UI to edit the albums config and generate player and index HTML for multiple albums

positional arguments:
  config_file          Albums config file path
  dir_path             Albums directory path

options:
  -h, --help           show this help message and exit
  --host host          Host to bind to, default: 127.0.0.1
  --port port          Port to bind to, default: 8000
  --trusted-host host  Add a trusted request hostname, can be specified multiple times, default: ['127.0.0.1', 'localhost']
  -v, --verbose        Increase verbosity level
```

## Disclaimer

1. This project is an open-source tool for personal learning and technical research only. It does not provide copyrighted music, pirated content, or cracking services.
2. Users must comply with local laws and regulations when using this project. This software does not encourage, support, or participate in any form of intellectual property or copyright infringement.
3. Any legal disputes, losses, or damages arising from the use of this project shall be borne solely by the user. The developer assumes no direct, indirect, or incidental legal liability.
4. If any content in this project, including features, source code, or asset files, infringes upon your legal rights, please contact the developer promptly. We will remove or modify it upon verification.

## License

MIT
