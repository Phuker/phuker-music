# phuker-music

[Demo](https://phuker.github.io/phuker-music/) | [GitHub](https://github.com/Phuker/phuker-music) | [PyPI](https://pypi.org/project/phuker-music/) | Readme ([English](https://github.com/Phuker/phuker-music/blob/main/Readme.md), 简体中文)

HTML 音乐播放器生成器。扫描音频文件目录，生成离线单文件 HTML 播放器。也可以通过 JSON 配置文件，为多张专辑批量生成播放器页面及索引页。你可以用浏览器直接打开生成的 HTML 文件，也可以将它们和音频文件一起在设备间同步，或上传到 Web 服务器使用。

您可以访问 [demo](https://phuker.github.io/phuker-music/) 直接查看索引页和播放器的生成效果。

## 典型使用场景

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

结果如下：

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
phuker-music albums-webui ./albums.json .
```

在浏览器中访问 <http://127.0.0.1:8000/>，将专辑从 Available 列拖拽到 Albums 列，点击顶部的 `Save & Generate` 按钮，结果如下：

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

## 功能特性

### 绝不存在的特性

- 无需账号登录和付费订阅
- 没有 15 秒试听限制
- 没有开屏广告
- 没有贷款广告弹窗
- 没有 AI
- 没有追踪、分析、统计或遥测
- 不上传任何用户数据
- 没有额外资源 — 无 JS/CSS 依赖、无网络字体、无 CDN
- **只有一个 HTML 文件**

### 现有特性

- 系统原生媒体控制与播放信息展示
- 每首曲目开始播放时弹出系统通知（需要授予权限）
- 可被安装为渐进式 Web 应用（PWA）
- 暗色模式跟随系统
- 后台播放防止冻结

### 暂未支持

- 无缝播放

## 安装与运行

运行本项目需要 Python 3.10 或更高版本。

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

## 用法

```console
$ phuker-music --help
用法：phuker-music [-h] [-v] [-V] command ...

音乐播放器 HTML 生成器

位置参数：
  command
    player        为单张专辑生成音乐播放器 HTML
    albums        为多张专辑生成播放器和索引页 HTML
    albums-webui  启动 Web UI 以编辑多张专辑配置并生成播放器和索引页 HTML

可选参数：
  -h, --help      显示此帮助信息并退出
  -v, --verbose   增加日志详细程度
  -V, --version   显示版本号并退出
```

```console
$ phuker-music player --help
用法：phuker-music player [-h] [-t title] [-c file] [--player-filename filename] [-r] [--sort-type type] [-f] [-v] dir_path

为单张专辑生成音乐播放器 HTML

位置参数：
  dir_path                    专辑目录路径

可选参数：
  -h, --help                  显示此帮助信息并退出
  -t, --title title           专辑标题，默认：目录名
  -c, --cover file            专辑封面文件路径，相对于 dir_path
  --player-filename filename  播放器文件名，默认：player.html
  -r, --recursively           递归扫描子目录中的音频文件
  --sort-type type            排序方式，可选：filename, mtime_desc，默认：filename
  -f, --force                 若播放器文件已存在则覆盖
  -v, --verbose               增加日志详细程度
```

```console
$ phuker-music albums --help
用法：phuker-music albums [-h] [-f] [-v] config_file

为多张专辑生成播放器和索引页 HTML

位置参数：
  config_file    多张专辑配置文件路径

可选参数：
  -h, --help     显示此帮助信息并退出
  -f, --force    若索引页和播放器文件已存在则覆盖
  -v, --verbose  增加日志详细程度
```

```console
$ phuker-music albums-webui --help
用法：phuker-music albums-webui [-h] [--host host] [--port port] [--trusted-host host] [-v] config_file dir_path

启动 Web UI 以编辑多张专辑配置并生成播放器和索引页 HTML

位置参数：
  config_file          多张专辑配置文件路径
  dir_path             多张专辑目录路径

可选参数：
  -h, --help           显示此帮助信息并退出
  --host host          绑定的主机地址，默认：127.0.0.1
  --port port          绑定的端口，默认：8000
  --trusted-host host  添加受信任的请求主机名，可多次指定，默认：['127.0.0.1', 'localhost']
  -v, --verbose        增加日志详细程度
```

## 免责声明

1. 本项目是一个开源的、仅用于个人学习和技术研究的工具，不提供受版权保护的音乐、盗版内容或破解服务。
2. 用户在使用本项目时，必须遵守当地的法律法规。本软件不鼓励、不支持、也不参与任何形式的侵犯知识产权或版权的行为。
3. 任何个人或组织因使用本项目而导致的任何法律纠纷、损失或损害，均由使用者自行承担，开发者不承担任何直接、间接或附带的法律责任。
4. 如果本项目中的任何内容（包括功能、代码或资产文件）侵犯了您的合法权益，请及时联系开发者，我们将在确认后第一时间进行删除或修改。

## 许可证

MIT
