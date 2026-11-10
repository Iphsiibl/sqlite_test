# sqlite

基于 Python 标准库 `sqlite3` 的数据访问层示例项目。

## 环境配置（uv）

本项目使用 [uv](https://docs.astral.sh/uv/) 管理 Python 解释器与虚拟环境。

### 1. 前置条件

```powershell
uv --version   # 需要 uv >= 0.13.7（构建后端 uv_build 的要求）
```

### 2. 安装项目要求的 Python 版本

`pyproject.toml` 要求 `requires-python = ">=3.14"`，`.python-version` 固定为 `3.14`。
若本机没有 3.14，用 uv 下载托管版本：

```powershell
uv python install 3.14
```

输出示例：

```
Installed Python 3.14.8 in 42ms
 + cpython-3.14.8-windows-x86_64-none (python3.14.exe)
```

### 3. 创建虚拟环境并同步依赖

```powershell
uv sync
```

`uv sync` 会完成三件事：

1. 依据 `.python-version` / `requires-python` 选择 CPython 3.14.8；
2. 在项目根目录创建 `.venv` 虚拟环境；
3. 解析并安装依赖，同时构建本地包 `sqlite==0.1.0`（后端 `uv_build`），生成 `uv.lock`。

输出示例：

```
Using CPython 3.14.8
Creating virtual environment at: .venv
Resolved 1 package in 4ms
   Building sqlite @ file:///D:/code/sqlite
      Built sqlite @ file:///D:/code/sqlite
Prepared 1 package in 54ms
Installed 1 package in 15ms
 + sqlite==0.1.0 (from file:///D:/code/sqlite)
```

### 4. 验证环境

```powershell
uv run python --version        # Python 3.14.8
uv run python database.py      # 创建 demo.db，插入 users / orders 各 5 行
uv run python -c "import sqlite"   # 导入 sqlite.py，模块末尾调用 ensure_ready()
uv run sqlite                  # 运行 [project.scripts] 入口
```

`sqlite.py` 在被导入时自动执行 `ensure_ready()`，依据 `schema.sql` 创建
`yuejiao.db` 并写入种子数据，实测生成 12 张表：`sys_user`、`student_admin_service`、
`student_psych_profile`、`student_psych_alert`、`student_feedback_ticket`、`crm_lead`、
`employee_daily_report`、`student_score`、`course_project`、`event_lecture`、
`event_registration`、`conversation_log`。

## 常用命令

| 命令 | 说明 |
| --- | --- |
| `uv sync` | 创建/更新 `.venv` 并同步依赖 |
| `uv add <包名>` | 新增依赖并更新 `pyproject.toml` 与 `uv.lock` |
| `uv remove <包名>` | 移除依赖 |
| `uv run <命令>` | 在虚拟环境中运行命令（自动使用 `.venv`） |
| `uv run python xxx.py` | 运行脚本 |
| `uv pip list` | 查看已安装的包 |
| `uv python list` | 查看可用的 Python 版本 |
| `uv lock` | 仅更新锁文件，不安装 |

## 说明

- `.venv` 已加入 `.gitignore`，不会被提交。
- `uv.lock` 应提交到版本库，保证团队环境一致。
- 首次执行 `uv sync` 时可能出现 hardlink 失败的警告（Windows 跨盘符时常见），
  属正常回退为文件拷贝，不影响使用；可用 `UV_LINK_MODE=copy` 消除。
