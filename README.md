# MyDalamudPlugins

个人 Dalamud 插件仓库，通过 GitHub Actions 自动从多个上游源同步插件元数据并定时更新。

> ⚠️ 自用仓库，使用需自行承担风险。

## 配置

编辑 `updater/origin_repo.json` 管理插件源：

```json
{
  "plugins": ["Plugin Name"],
  "source_repo": "https://github.com/org/repo",
  "source_url": "https://source-url/pluginmaster.json",
  "enabled": true
}
```
