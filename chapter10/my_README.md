# uv

> [!Note] uv 笔记
> `uv` 是 Astral 公司采用 Rust 编写的极速 Python 包和项目管理器，旨在替代 `pip`、`pip-tools`、`pipx`，甚至 `poetry`、`virtualenv` 和 `pyenv` 等工具。最大的优势在于其令人难以置信的性能（比现有的工具快数倍甚至数十倍）。

## 项目管理

`uv` 提供了类似 Cargo 或 Poetry 的基于 `pyproject.toml` 的现代项目管理体验。这是开发复杂 Python 应用的最佳实践。

### 初始化与创建

```bash
# 在当前目录初始化一个新项目（生成 pyproject.toml 和 .python-version）
uv init

# 在指定目录创建新项目
uv init my_project

# 指定 python 版本初始化
uv init --python 3.13
```

### 添加与移除依赖

```bash
# 添加依赖包（写入 dependencies）
uv add requests

# 添加特定版本的依赖
uv add "requests==2.31.0"
uv add "pandas>=2.0.0"

# 批量安装 requirement.txt 中的依赖
uv add -r requirement.txt

# 移除依赖包
uv remove requests
```

### 依赖查看与锁定

```bash
# 检查当前项目的可读依赖树（极大方便排查依赖冲突与重型包）
uv tree

# 仅查看顶级层依赖不展开子依赖树
uv tree --depth 1

# 检查当前项目的约束并生成/刷新 uv.lock 锁定文件
uv lock

# 约束范围内，尽可能把全部依赖升级到最新，并更新 uv.lock
uv lock --upgrade

# 针对指定包单独执行版本更新（修改锁文件）
uv lock --upgrade-package requests
```

### 环境同步

```bash
# 根据 uv.lock 严格同步当前项目的依赖环境（自动创建 .venv 并多退少补）
uv sync
```

### 运行脚本与命令

```bash
# 在项目的严格虚拟环境中运行 Python 脚本
uv run xxx.py
uv run python -m http.server

# 自动透传执行安装的环境模块（如 fastapi, pytest, black 等）
uv run pytest
uv run ruff format

# 传递临时环境变量运行命令
PORT=8000 uv run fastapi dev
```

### 构建与发布

```bash
# 将你的项目打包构建为 sdist (源码包) 和 wheel (预编译包)，产出到 dist/ 目录
uv build

# 将当前已构建好的包发布至 PyPI 或私有 PyPI 源
uv publish
```

## 包管理 (替代 pip)

若只想单纯将 `uv` 作为极快的包安装工具（替代 pip 核心功能），可以使用 `uv pip` 接口，它的体验和 `pip` 基础保持一致。

### 安装与卸载

```bash
# 下载并安装包
uv pip install xxx

# 根据 requirements.txt 安装依赖
uv pip install -r requirements.txt

# 卸载包
uv pip uninstall xxx
```

### 查看包

```bash
# 查看已安装的包列表
uv pip list

# 查看指定包的具体信息
uv pip show xxx

# 查看依赖依赖树
uv pip tree

# 导出当前环境已安装的包到 requirements.txt
uv pip freeze > requirements.txt
```

### 编译与解析 (替代 pip-tools)

```bash
# 将 requirements.in 或者 pyproject.toml 锁定并编译为 requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# 同步环境（确保环境中的包和锁定的 requirements.txt 严格一致，多退少补）
uv pip sync requirements.txt
```

## 环境管理 (替代 virtualenv)

`uv` 可以用来创建极其快速的虚拟环境。

```bash
# 在当前目录下创建名为 .venv 的默认虚拟环境
uv venv

# 创建指定名称的虚拟环境
uv venv my_env

# 指定 Python 版本并创建虚拟环境
uv venv --python 3.9
```

## Python 版本管理 (替代 pyenv)

`uv` 会预设并自动下载、管理所需的由于没有存在系统里的各个不同的短板 Python 版本。

```bash
# 查看所有可用的/已安装的 Python 版本
uv python list

# 安装指定的 Python 版本
uv python install 3.10 3.12

# 定位当前目录将会使用的 Python 解析器路径
uv python find

# 指定当前目录应当使用的 Python 版本（会写入 .python-version 文件）
uv python pin 3.11
```

## 全局工具管理 (替代 pipx)

如果你希望在独立环境中执行某些提供 CLI 接口的包（如 `ruff`, `httpie`, `black` 等）却不希望污染系统或者基础应用的依赖环境，可以利用 `uv tool` 及 `uvx`。

```bash
# 临时运行某个工具（不安装它，直接运行并自动随后销毁其环境）
uvx ruff check .
# 或使用完整别名
uv tool run ruff check .

# 在独立的环境中全局安装一个工具并将其暴露在 PATH 中
uv tool install ruff

# 升级已安装的全局工具
uv tool upgrade ruff

# 卸载全局工具
uv tool uninstall ruff

# 列出所有已安装的全局工具列表
uv tool list
```

## 缓存管理

```bash
# 清理 uv 的包缓存
uv cache clean

# 打印显示缓存目录对应的具体位置
uv cache dir
```

> [!Tip] 使用建议
> 1. 如果你在管理一个完整的后端应用或库包，优先推荐使用 `uv run` 和 `uv add` 来进行项目级生命周期的工作，避免手动敲击冗长的 `pip` 或手动激活虚拟环境。
> 2. `uv` 非常方便的一点在于其可以使用 `uvx` 临时执行全局 Python 工具并省去复杂的处理依赖冲突的麻烦（如 `uvx ruff`）。
> 3. 在迁移老旧项目时，如果你暂时只想享受它更快的安装速度，并不想触碰依赖图的管理模式，你只需使用 `uv venv` 和 `uv pip install` —— 它比原本的方案会快上好几个数量级！
