# 项目概览

音乐播放器 HTML 生成器：扫描音频文件目录，生成带播放功能的单页 HTML。

- `phuker_music/` — Python 包（`pip install -e .` 提供 `phuker-music` 命令）
  - `cli.py` — argparse CLI，`player`、`albums`、`albums-webui` 三个子命令
  - `player.py` — 单专辑生成，`normalize_album_config()`、`generate()`
  - `albums.py` — 多专辑批量生成 + 索引页，`normalize_albums_config()`、`main()`
  - `albums_webui.py` — Flask 应用，`/api/scan`、`/api/save-config`、`/api/generate`
  - `utils.py` — `assert_()`、日志初始化（TTY 彩色）、语种识别、Jinja2 环境、`os_path`、路径工具函数
  - `constants.py` — `AUDIO_EXT_LIST`、`IMAGE_EXT_LIST`、默认配置常量
  - `templates/` — Jinja2 模板（`player.html`、`albums.html`）
  - `static/` — 静态资源（`css/`、`js/`、`images/`、`audio/`、`libs/`、`albums_webui.html`），`libs/` 下为本地化第三方库，无需读取
- `docs/` — 演示音频样本 + `albums.json`
- `tests/` — 单元测试，fixture 目录结构：`tests/files/config/albums.test.json`（配置）+ `tests/files/albums/`（音频和封面图片文件）

# 开发命令

```bash
pip install -U -r requirements.txt    # 安装依赖
pip install -e .                      # 或 make dev-install，editable 开发安装
make test                             # 运行测试：先 unittest，再 CLI 集成测试（albums 子命令）
make demo                             # 等价于 phuker-music albums -v -f ./docs/albums.json
make build                            # 构建 wheel 和 sdist（需 uv/uvx）
```

# 核心架构

## `generate()` — `player.py:155`

```python
def generate(album_config: dict, *, base_dir_path: str = '.', overwrite: bool = False) -> None:
```

- 第一个参数为 `album_config` 字典，不展开为独立 kwargs
- 内部首先调用 `normalize_album_config(album_config, base_dir_path=base_dir_path)` 校验和标准化（默认 `absolute=True`，返回绝对路径）
- **`overwrite` 不在 `album_config` 字典中**，是独立参数
- `album_config` 字段顺序：`album_dir_path`、`title`、`cover_file`、`player_filename`、`recursively`、`sort_type`，各调用点、CLI 参数声明、保存配置文件均保持此顺序

## `normalize_album_config()` — `player.py:111`

```python
def normalize_album_config(album_config_input: dict, *, base_dir_path: str = '.', absolute: bool = True) -> dict:
```

- `absolute=True` 返回绝对路径，`absolute=False` 返回相对路径（用于 `albums_webui.py` 保存配置文件）
- **不包含**限制 `album_dir_path` 在 `base_dir_path` 范围内的安全校验（仅 `albums.py:normalize_albums_config()` 有此检查）

## `normalize_albums_config()` — `albums.py:16`

```python
def normalize_albums_config(albums_config: dict, *, albums_config_dir_path: str, absolute: bool = True) -> dict:
```

- `albums_config_dir_path` 是配置文件所在目录的绝对路径
- 函数内部从 `albums_config['albums_dir_path']`（相对路径）解析出绝对路径
- `albums_config['albums_index_filename']` 仅为文件名（不含 `/` `\`），与 `albums_dir_path` 拼接得到输出路径 `albums_index_file_path`
- `absolute=False` 时将路径转回相对于 `albums_config_dir_path` 的路径
- 每个 album 的 `album_dir_path` 必须位于 `albums_dir_path` 内（`is_sub_path` 检查）

## Albums 配置格式

```json
{
    "albums_dir_path": "../albums",
    "albums_index_filename": "index.html",
    "albums": [
      {
        "album_dir_path": "./Ambience",
        "title": "Ambience",
        "cover_file": "./Cover.jpg",
        "player_filename": "player.html",
        "recursively": false,
        "sort_type": "filename"
      }
    ]
}
```

- `albums_dir_path` — 相对于配置文件所在目录；支持 `../` 指向其他目录
- `albums_index_filename` — 仅文件名，不允许含 `/` `\`
- `albums` 中每个 `album_config`：
  - `album_dir_path` - 相对于 `albums_dir_path`
  - `cover_file` - 相对于 `album_dir_path`，必须位于 `album_dir_path` 内
  - `player_filename` - 仅文件名，不允许含 `/` `\`

## 模板数据

**`player.html` 模板变量**（`player.py:173-179`）：

- `lang` — 语种代码
- `title` — 专辑标题
- `cover_file` — 相对路径或 `None`
- `music_info_groups` — `[{name: str, music_info_sub_list: [{index, path, name, file_size_str, duration_str}]}]`
- `music_info_list` — `music_info_groups` 展平后的 list
- `storage_key_prefix` — localStorage key 前缀

**`albums.html` 模板变量**（`albums.py:85`）：

- `lang` — 语种代码
- `manifest_url` — Web App Manifest data URL
- `indexes` — `[(player_path, title, cover_path), ...]`

# 路径工具

## `os_path` — `utils.py:85-88`

- Unix 上等于 `os.path`，Windows 上为 `OsPathProxy()` 实例（斜杠标准化，将 `\` 替换为 `/`）
- **所有 `os.path` 调用必须使用 `os_path` 替代**

| 函数 | 用途 |
|------|------|
| `get_abs_joined_path(*paths)` | expanduser → join → abspath → 斜杠标准化 |
| `get_rel_path(path, start_dir_path)` | expanduser → relpath → 斜杠标准化，以 `./` 开头 |
| `is_sub_path(path, parent_path)` | `os_path.commonpath` 判断路径是否在目录范围内 |
| `assert_(expr, msg)` | 抛出 `AssertionError`（不是 `ValueError`） |

# 路径逃逸限制

- **`album_config`**：`cover_file` 必须位于 `album_dir_path` 内（`player.py:141`），`player_filename` 不能包含 `/` 或 `\`（`player.py:126`）
- **`albums_config`**：每个 `album_dir_path` 必须位于 `albums_dir_path` 内（`albums.py:29-32`）
- **`player` CLI**：无路径逃逸限制（`normalize_album_config` 不做 `is_sub_path` 检查于 `base_dir_path` 范围）

# 其他注意事项

- **`-v` / `--verbose`** — 顶层和子命令级 `-v` 叠加，`>=1` 即设 `DEBUG`（`cli.py:122-124`）
- **封面文件不存在时抛 `AssertionError`**（不是 `FileNotFoundError`）— `player.py:142`
- **Jinja2 `autoescape=True`** — HTML 模板默认转义；`| safe_json_encode` 过滤器额外替换 `<` `>` 防 XSS
- **Jinja globals**: `read_static_text_file(path)`、`read_static_file_as_data_url(path, mime)` — 以 `phuker_music/static/` 为基准
- **语种识别** — 置信度 >0.98 才采纳，否则回退 `en`；跳过低置信 `la`；输入小写化避免全大写 bug；`langid` 懒加载
- **Sort types**：`filename`（默认）、`mtime_desc`
- **无 lint/typecheck/formatter 配置**
- **测试 `mtime_desc` 排序** — Makefile 中 `make test` 先 touch 测试文件设置固定 mtime，再运行测试
- **`albums-webui` CLI** — 需两个位置参数：`<albums_config_file_path> <albums_dir_path>`
- **`albums_webui` 线程** — scan 和 generate 使用 `threading.Lock` + daemon thread，模块级全局状态（`scan_status`、`generate_status`）
- **CSS 规范** — font-size 使用绝对大小关键字（`large`/`medium`/`small`/`x-large`），不硬编码 px；albums_webui.css 中 font-family 使用 CSS 变量 `var(--font-ui)`/`var(--font-mono)`
- **CSS 隐藏滚动条** — 使用两个规则 `scrollbar-width: none` + `::-webkit-scrollbar { display: none }`，player 中 `ul`、`li.item`、`span.music_name` 均遵循此模式
- **player 前端 `li.item` 结构** — 为 flex 容器，歌曲名包在 `span.music_name` 可独立横向滚动（`flex: 1; min-width: 0`），`span.metadata` 始终靠右可见（`flex-shrink: 0`）
