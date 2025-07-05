# Dalamud Plugin Repository Updater

这是一个用于自动获取和更新Dalamud插件信息的Python脚本。

## 功能特性

- 从多个插件源自动获取插件信息
- 支持多种URL格式（GitHub raw、releases、API等）
- 自动合并和去重插件列表
- 保持现有插件信息，只更新目标插件

## 安装和使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置插件源

编辑 `origin_repo.ini` 文件，格式如下：

```ini
# 插件名1, 插件名2, 插件名3
插件源URL

# Something Need Doing
https://puni.sh/api/repository/croizat

# ReAction
# https://github.com/UnknownX7/ReAction
https://raw.githubusercontent.com/UnknownX7/DalamudPluginRepo/master/pluginmaster.json

# Chat Two
https://github.com/goatcorp/PluginDistD17/blob/main/stable/ChatTwo/ChatTwo.json
# 从该路径下载 https://raw.githubusercontent.com/goatcorp/PluginDistD17/refs/heads/main/stable/ChatTwo/latest.zip 到plugins目录，并且重命名为chat2.zip
```

### 3. 运行脚本

```bash
python plugin_updater.py
```

脚本会：
1. 读取 `origin_repo.ini` 配置文件
2. 从各个源获取插件数据
3. 查找指定的目标插件
4. 处理特殊下载任务（如直接下载zip文件）
5. 合并到 `myrepo.json` 文件中

## 配置文件格式

配置文件支持以下格式：

- 注释行：以 `#` 开头，可以包含插件名称（用逗号分隔）或仓库信息
- URL行：插件源的URL地址
- 特殊下载任务：格式为 `# 从该路径下载 URL 到目录名 并且重命名为 文件名`

支持的URL类型：
- GitHub raw文件链接
- GitHub tree/blob链接（自动转换）
- API端点
- 标准JSON文件
- plogon插件页面（暂不支持，会跳过）

特殊功能：
- 支持直接下载zip文件到指定目录
- 自动处理多种GitHub链接格式
- 智能插件名称匹配（支持Name和InternalName）

## 输出格式

生成的 `myrepo.json` 文件包含标准的Dalamud插件信息：

```json
[
  {
    "Author": "作者名",
    "Name": "插件名称", 
    "Punchline": "简短描述",
    "Description": "详细描述",
    "Tags": ["标签"],
    "InternalName": "内部名称",
    "AssemblyVersion": "版本号",
    "RepoUrl": "仓库地址",
    "ApplicableVersion": "适用版本",
    "DalamudApiLevel": 12,
    "DownloadLinkInstall": "下载链接",
    "DownloadLinkUpdate": "更新链接"
  }
]
```

## 错误处理

脚本包含完整的错误处理：
- 网络请求超时和失败
- JSON解析错误
- 文件读写错误
- 缺失插件的提示

## 注意事项

1. 某些GitHub releases页面和特殊插件页面可能需要手动处理
2. 网络请求有10秒超时限制
3. 脚本会保留现有插件，只更新目标插件
4. 建议运行前备份现有的 `myrepo.json` 文件
