# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

个人 Dalamud 插件仓库自动化系统，用于管理 Final Fantasy XIV 的 Dalamud 插件。从多个上游源（puni.sh、GitHub raw JSON、自定义 API）抓取指定插件元数据，合并到 `myrepo.json`，通过 GitHub Actions 自动定时更新并提交。

## Running Commands

```bash
# 安装依赖
pip install -r updater/requirements.txt

# 本地运行插件更新（在 updater/ 目录下执行）
cd updater && python plugin_updater.py
```

无测试套件，无 linter 配置。

## Architecture

```
/
├── updater/                    # 脚本、配置、依赖
│   ├── plugin_updater.py       # 主脚本
│   ├── origin_repo.json        # 插件源配置
│   └── requirements.txt        # Python 依赖
├── .github/workflows/          # GitHub Actions 工作流
├── myrepo.json                 # 生成的插件仓库数据（产物，不要手动编辑）
├── CLAUDE.md
└── README.md
```

核心是 `PluginUpdater` 类（[plugin_updater.py](updater/plugin_updater.py)），流程为：

1. **`load_config()`** — 解析 [origin_repo.json](updater/origin_repo.json)，按 `enabled` 字段过滤，建立 `plugin_name → source_url` 映射
2. **`update_plugins()`** — 对每个目标插件，从其源 URL 获取 JSON 数据，按 `Name`/`InternalName` 匹配，合并 `extra_fields`
3. **`merge_plugins()`** — 与现有 `myrepo.json` 按 `AssemblyVersion` 比对，版本变化则更新，新增则添加
4. **`save_plugins()`** — 写入 `../myrepo.json`

### Configuration File Format (`origin_repo.json`)

JSON 数组，每个条目代表一个插件源：

```json
{
  "plugins": ["Plugin Name A", "Plugin Name B"],
  "source_repo": "https://github.com/org/repo",
  "source_url": "https://source-url/pluginmaster.json",
  "enabled": true,
  "extra_fields": { "DownloadLinkInstall": "..." }
}
```

- `plugins` (string[]) — 要从该源抓取的插件名列表
- `source_repo` (string?) — 上游仓库/网站地址，仅用于维护参考
- `source_url` (string) — 返回 JSON 插件元数据的数据源 URL
- `enabled` (bool) — `false` 跳过该源，等效于原来的注释掉
- `extra_fields` (object?) — 可选，合并到抓取到的插件数据中的额外字段

### GitHub Actions Workflows

- **基础版** ([update-plugins.yml](.github/workflows/update-plugins.yml)) — push/PR/定时触发，简单执行+提交
- **增强版** ([update-plugins-enhanced.yml](.github/workflows/update-plugins-enhanced.yml)) — 仅手动触发，含备份恢复、JSON 验证、变更统计、日志 artifact

定时运行 cron：`0 0,12 * * *`（UTC），时区 Asia/Shanghai。push 触发时忽略 `myrepo.json`、`*.md` 的变更以防循环。

### Plugin Sources

所有数据源均返回 JSON 格式的插件元数据，支持的来源：
- `raw.githubusercontent.com` 上的 `pluginmaster.json` / `repo.json`
- puni.sh API（`puni.sh/api/repository/*`、`puni.sh/api/plugins`）
- 自定义端点（`plogon.meowrs.com`、`love.puni.sh`）
- GitHub `/blob/` 和 `/tree/` URL 自动转换为 raw URL

## Key Conventions

- 所有输出和注释为中文
- `myrepo.json` 是生成的产物文件，不要手动编辑
- 添加新插件时在 `updater/origin_repo.json` 数组中添加新条目，设 `"enabled": true`
- 禁用插件不删除条目，改为 `"enabled": false`
