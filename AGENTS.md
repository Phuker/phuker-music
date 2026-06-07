# 项目概览

音乐播放器 HTML 生成器：扫描音频文件目录，生成带播放功能的单页 HTML。

- `phuker_music/` — Python 包（`pip install -e .` 可安装，提供 `phuker-music` 命令）
  - `cli.py` — argparse CLI，包含 `player` 和 `albums` 两个子命令
  - `player.py` — 单专辑播放器生成核心逻辑（`get_music_groups()`, `generate()`）
  - `albums.py` — 多专辑批量生成 + 索引页生成
  - `utils.py` — `_assert` 辅助函数、日志初始化（TTY 彩色日志）、语种识别、Jinja2 环境
  - `__main__.py` — 支持 `python -m phuker_music`
  - `templates/` — Jinja2 模板（`player.html`, `albums.html`）
  - `static/` — 静态资源（`css/`, `js/`, `images/`, `audio/`）
- `docs/` — 演示用音频样本目录 + 配置文件 `albums.json`（运行 `make demo` 生成索引页 `docs/index.html` 和每张专辑播放器）
- `tests/` — 单元测试，依赖 `tests/files/` 下的测试用音频文件

# 开发命令

```bash
# 安装依赖
pip install -r requirements.txt

# 开发安装（editable），提供 phuker-music 命令
make dev-install
# 或直接运行：
pip install -e .

# 运行方式
python -m phuker_music player <dir> -t "Title" ...
phuker-music player <dir> -t "Title" ...   # 需先 pip install -e .

# 运行测试（单元测试 + CLI 集成测试）
make test

# 构建 + 安装发布包（构建需要 uv/uvx）
make build     # 使用 uvx 运行 pyproject-build
make install   # pip install dist/*.whl

# 生成演示页面
make demo      # 等价于: python -m phuker_music albums -v -f ./docs/albums.json
```

# 注意事项

- **`player.generate()` 的 `album_dir_path` 不能以 `/` 或 `\` 结尾** — `player.py:123` 有 `_assert` 校验；但 CLI（`cli.py:23`）和 albums 配置（`albums.py:35`）会先经 `os.path.abspath()` 自动去掉尾部斜杠，所以正常使用不会触发
- **`output_filename` 不能包含 `/` 或 `\`** — `player.py:124` 有校验，CLI 和 albums 两条路径都受保护；CLI 通过 `-o`/`--output-filename` 指定，默认 `player.html`
- **`generate()` 参数顺序**: `album_dir_path, title, cover_file, output_filename, recursively, sort_type, overwrite` — 各调用点、CLI 参数声明顺序均保持一致
- **`utils._assert()` 抛出 `AssertionError`**，不是 `ValueError` — 如果捕获异常，注意类型
- **`-v` / `--verbose` 启用调试日志** — 顶层和子命令级 `-v` 叠加，`>=1` 即设 `DEBUG` 级别（`cli.py:109`）
- **`--force` / `-f`** — 输出文件已存在会报 `FileExistsError`（报错信息中会提示使用 `-f`），加 `-f` 强制覆盖
- **Albums 命令每张专辑默认 `overwrite: True`** — 与 `player` CLI 默认 `overwrite=False` 不同；`phuker_music/albums.py` 的 `main()` 对索引页仍使用顶层的 `--force` 参数
- **Jinja2 `autoescape=True`** — HTML 模板默认转义；`|json_encode` 过滤器额外替换 `<` `>` 防 XSS
- **`read_file()` 和 `read_file_as_data_url()` 以 `phuker_music/static/` 为基准路径**（`utils.py:get_jinja_env()`，基于 `__file__` 解析）
- **语种识别 quirks** — 置信度 >0.98 才采纳，否则回退 `en`；跳过低置信的 `la`；输入会被小写化以避免全大写文本的识别 bug（`langid` 库懒加载，首次调用较慢）
- **Sort types**: `filename`（默认）、`mtime_desc`
- **支持音频格式**: `.mp3`, `.ogg`, `.flac`, `.m4a`, `.wav`, `.weba`
- **Album 配置文件**格式示例见 `tests/files/albums.test.json` 和 `docs/albums.json`，`album_dir_path`/`albums_index_file_path` 均相对于配置文件所在目录解析
- **albums 配置中 `album_dir_path` 和 `albums_index_file_path` 不能逃逸出 `albums_dir_path`** — `normalize_album_config()` 和 `normalize_albums_config()` 中用 `os.path.commonpath()` 校验，防止通过 `..`、绝对路径等方式导致路径穿越
- **无 lint/typecheck/formatter 配置** — 本仓库没有预配置的代码检查工具
