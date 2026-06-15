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

## 安装与运行

### 用 uvx 运行（无需安装）

```bash
uvx phuker-music --help
```

### 用 pipx 运行（无需安装）

```bash
pipx run phuker-music --help
```

### 用 uv 安装并运行

```bash
uv tool install phuker-music
phuker-music --help
```

### 用 pipx 安装并运行

```bash
pipx install phuker-music
phuker-music --help
```

### 用 pip 安装并运行

```bash
pip install phuker-music
phuker-music --help
```

## 快速开始

### 为单张专辑生成音乐播放器 HTML

首先 `cd` 进入包含音频文件的目录，例如以下目录中包含 1 张封面图片和 3 个音频文件：

```text
.
|-- Cafe ambience.m4a
|-- Cover.jpg
|-- Crowd Talking Quietly Stadium.mp3
`-- Distant train with cicadas.m4a
```

然后运行：

```bash
phuker-music player --force --cover Cover.jpg .
```

你将会得到：

```text
.
|-- Cafe ambience.m4a
|-- Cover.jpg
|-- Crowd Talking Quietly Stadium.mp3
|-- Distant train with cicadas.m4a
`-- player.html                        <-- 播放器 HTML 文件
```

在浏览器中打开 `player.html` 即可使用播放器。

### 为多张专辑生成播放器和索引页

`cd` 进入包含多个专辑目录的目录，例如以下目录中包含 2 个专辑目录：

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

然后运行：

```bash
phuker-music albums-webui ./albums.json
```

在浏览器中访问 <http://127.0.0.1:8000/>，将专辑从 Available 列拖拽到 Albums 列，点击顶部的 `Save & Generate` 按钮，你将会得到：

```text
.
|-- albums.json                                            <-- 配置文件
|-- Ambience
|   |-- Cafe ambience.m4a
|   |-- Cover.jpg
|   |-- Crowd Talking Quietly Stadium.mp3
|   |-- Distant train with cicadas.m4a
|   `-- player.html                                        <-- 播放器 HTML 文件
|-- index.html                                             <-- 索引 HTML 文件
`-- Nature
    |-- Cover.jpg
    |-- FL Mocking birds.mp3
    |-- Frogs and nature in Southern Brasil in August.m4a
    |-- Morning birds.m4a
    |-- Nature.m4a
    |-- player.html                                        <-- 播放器 HTML 文件
    |-- Rain.ogg
    `-- Thunder.mp3
```

在浏览器中打开 `index.html` 即可访问索引页。

## 用法

```console
$ phuker-music --help
usage: phuker-music [-h] [-v] [-V] command ...

Music player HTML generator

positional arguments:
  command
    player        为单张专辑生成音乐播放器 HTML
    albums        为多张专辑生成播放器和索引页 HTML
    albums-webui  启动 Web UI 以编辑专辑配置并生成播放器和索引页 HTML

options:
  -h, --help      显示此帮助信息并退出
  -v, --verbose   增加日志详细程度
  -V, --version   显示版本号并退出
```

```console
$ phuker-music player --help
usage: phuker-music player [-h] [-t title] [-c file] [-o filename] [-r] [--sort-type type] [-f] [-v] dir_path

为单张专辑生成音乐播放器 HTML

positional arguments:
  dir_path                        专辑目录路径

options:
  -h, --help                      显示此帮助信息并退出
  -t, --title title               专辑标题，默认：目录名
  -c, --cover file                专辑封面文件路径，相对于 dir_path
  -o, --output-filename filename  输出文件名，默认：player.html
  -r, --recursively               递归扫描子目录中的音频文件
  --sort-type type                排序方式，默认：filename，可选：filename, mtime_desc
  -f, --force                     若输出文件已存在则覆盖
  -v, --verbose                   增加日志详细程度
```

```console
$ phuker-music albums --help
usage: phuker-music albums [-h] [-f] [-v] config_file

为多张专辑生成播放器和索引页 HTML

positional arguments:
  config_file    专辑配置文件路径

options:
  -h, --help     显示此帮助信息并退出
  -f, --force    若输出文件已存在则覆盖
  -v, --verbose  增加日志详细程度
```

```console
$ phuker-music albums-webui --help
usage: phuker-music albums-webui [-h] [--host HOST] [--port PORT] [-v] config_file

启动 Web UI 以编辑专辑配置并生成播放器和索引页 HTML

positional arguments:
  config_file    专辑配置文件路径

options:
  -h, --help     显示此帮助信息并退出
  --host HOST    绑定的主机地址，默认：127.0.0.1
  --port PORT    绑定的端口，默认：8000
  -v, --verbose  增加日志详细程度
```

## 许可证

MIT
