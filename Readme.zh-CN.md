# phuker-music

[Demo](https://phuker.github.io/phuker-music/) | [GitHub](https://github.com/Phuker/phuker-music) | [PyPI](https://pypi.org/project/phuker-music/) | Readme ([English](https://github.com/Phuker/phuker-music/blob/main/Readme.md), 简体中文)

HTML 音乐播放器生成器。扫描音频文件目录，生成离线单文件 HTML 播放器。也可以通过 JSON 配置文件，为多张专辑批量生成播放器页面及索引页。

您可以访问 [demo](https://phuker.github.io/phuker-music/) 直接查看索引页和播放器的生成效果。授予系统通知权限后，每首曲目开始播放时，会弹出系统通知。

## 功能特性

- 没有贷款广告或会员订阅弹窗
- 没有 AI
- 没有追踪、分析、统计或遥测
- 不上传任何用户数据
- 没有额外资源 — 无 JS/CSS 依赖、无网络字体、无 CDN
- **只有一个 HTML 文件**

## 快速开始

首先 `cd` 进入包含音频文件的目录，然后：

### 用 uvx 运行

```bash
uvx phuker-music player .
```

### 用 pipx 运行

```bash
pipx run phuker-music player .
```

### 用 uv 安装并运行

```bash
uv tool install phuker-music
phuker-music player .
```

### 用 pipx 安装并运行

```bash
pipx install phuker-music
phuker-music player .
```

### 用 pip 安装并运行

```bash
pip install phuker-music
phuker-music player .
```

## 用法

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
  config_file    Albums config file path

options:
  -h, --help     show this help message and exit
  -f, --force    Overwrite output file if it exists
  -v, --verbose  Increase verbosity level
```

## 许可证

MIT
