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
- `tests/` — 单元测试，依赖 `tests/files/` 下的测试用音频文件

# 开发命令

```bash
pip install -U -r requirements.txt    # 安装依赖
pip install -e .                      # 或 make dev-install，editable 开发安装
make test                             # 运行测试：先 unittest，再 CLI 集成测试（albums 子命令）
make demo                             # 等价于 phuker-music albums -v -f ./docs/albums.json
make build                            # 构建 wheel 和 sdist（需 uv/uvx）
```

# 核心架构

## `generate()` 签名和流程

```python
# player.py
def generate(album_config: dict, *, base_dir_path: str = '.', overwrite: bool = False) -> None:
```

- 第一个参数为 `album_config` 字典，不展开为独立 kwargs
- 内部首先调用 `normalize_album_config(album_config, base_dir_path=base_dir_path)` 校验和标准化（默认 `absolute=True`，返回绝对路径）
- **`overwrite` 不在 `album_config` 字典中**，是独立参数
- `album_config` 字段：`album_dir_path`、`title`、`cover_file`、`player_filename`、`recursively`、`sort_type`，各调用点、CLI 参数声明、保存配置文件均保持顺序一致

## `normalize_album_config()` — `player.py:111`

- 签名：`normalize_album_config(album_config_input: dict, *, base_dir_path: str = '.', absolute: bool = True) -> dict`
- `absolute=True` 返回绝对路径，`absolute=False` 返回相对路径
- `albums.py` 中通过 `player.normalize_album_config()` 调用
- `albums_webui.py` 保存配置时传 `absolute=False`，使 JSON 文件中路径为相对路径
- **不包含** `is_sub_path()` 限制 `base_dir_path` 范围内安全校验（仅 `albums.py:normalize_albums_config()` 有此检查）

## `base_dir_path` 参数

- `normalize_album_config` 和 `generate` 均有此参数，默认 `'.'`
- CLI `player` 命令：不显式传递，使用默认值
- `albums.main()`：显式传递 `os_path.dirname(albums_config_file_path)`

# 路径工具

## `os_path` — `utils.py:85-88`

- Unix 上等于 `os.path`，Windows 上为 `OsPathProxy()` 实例（斜杠标准化，将 `\` 替换为 `/`）
- **所有 `os.path` 调用必须使用 `os_path` 替代**

## 关键工具函数（`utils.py`）

| 函数 | 用途 |
|------|------|
| `get_abs_joined_path(*paths)` | expanduser → join → abspath → 斜杠标准化 |
| `get_rel_path(path, start_dir_path)` | expanduser → relpath → 斜杠标准化，以 `./` 开头 |
| `is_sub_path(path, parent_path)` | `os_path.commonpath` 判断路径是否在目录范围内 |
| `assert_(expr, msg)` | 抛出 `AssertionError`（不是 `ValueError`） |

# 路径逃逸限制

- **`album_config` 中**：`cover_file` 必须位于 `album_dir_path` 内（`player.py:141`），`player_filename` 不能包含 `/` 或 `\`（`player.py:126`）
- **`albums_config` 中**：`albums_index_file_path` 和每个 `album_dir_path` 必须位于 `base_dir_path` 内（`albums.py:22, 28-31`）
- **`player` CLI**：无路径逃逸限制（`normalize_album_config` 不做 `is_sub_path` 检查）

# 其他注意事项

- **`-v` / `--verbose`** — 顶层和子命令级 `-v` 叠加，`>=1` 即设 `DEBUG`（`cli.py:122-124`）
- **`--force` / `-f`** — 输出文件已存在时抛 `FileExistsError`（提示使用 `-f`），加 `-f` 强制覆盖
- **封面文件不存在时抛 `AssertionError`**（不是 `FileNotFoundError`）— `player.py:142`
- **Jinja2 `autoescape=True`** — HTML 模板默认转义；`|json_encode` 过滤器额外替换 `<` `>` 防 XSS
- **`read_file()` / `read_file_as_data_url()`** — 以 `phuker_music/static/` 为基准路径
- **语种识别** — 置信度 >0.98 才采纳，否则回退 `en`；跳过低置信 `la`；输入小写化避免全大写 bug；`langid` 懒加载
- **Sort types**：`filename`（默认）、`mtime_desc`
- **Albums 配置格式**：示例见 `tests/files/albums.test.json` 和 `docs/albums.json`，`albums_index_file_path` 和 `album_dir_path` 路径相对于配置文件所在目录，`cover_file` 路径则相对于 `album_dir_path`
- **无 lint/typecheck/formatter 配置**
- **测试 `mtime_desc` 排序** — Makefile 中 `make test` 先 touch 测试文件设置固定 mtime，再运行测试
