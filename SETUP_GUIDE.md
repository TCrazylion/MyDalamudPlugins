# 🚀 GitHub Action 快速设置指南

## 📋 准备工作

所有必需文件已创建完成：
- ✅ `.github/workflows/update-plugins.yml` - 基础工作流
- ✅ `.github/workflows/update-plugins-enhanced.yml` - 增强工作流（可选）
- ✅ `plugin_updater.py` - 插件更新脚本
- ✅ `requirements.txt` - Python依赖
- ✅ `origin_repo.ini` - 插件源配置
- ✅ `test_github_action.py` - 配置测试脚本

## 🔧 GitHub 仓库设置

### 1. 推送代码到GitHub
```bash
git add .
git commit -m "Add GitHub Action for automated plugin updates"
git push origin main
```

### 2. 启用Actions权限 ⚠️ **重要**
1. 进入GitHub仓库
2. 点击 **Settings** 标签
3. 在左侧菜单选择 **Actions** → **General**
4. 在 "Workflow permissions" 部分：
   - 选择 ✅ **Read and write permissions**
   - 勾选 ✅ **Allow GitHub Actions to create and approve pull requests**
5. 点击 **Save** 保存设置

> **注意**: 如果跳过此步骤，Action将因权限不足而失败！

## ⚡ 运行方式

### 自动运行
- ⏰ **每天 UTC 00:00** 自动执行（北京时间 08:00）
- 🔄 自动检测插件更新并提交更改

### 手动运行
1. 进入仓库的 **Actions** 页面
2. 选择 "Update Dalamud Plugins" 工作流
3. 点击 **Run workflow** 按钮
4. 可选择是否强制更新

## 📊 监控和日志

### 查看运行状态
- 📍 **Actions页面**：实时查看工作流运行状态
- 📝 **详细日志**：点击具体运行查看详细步骤
- 📁 **Artifacts**：下载更新日志文件（保留30天）

### 运行结果
- ✅ **成功更新**：自动提交到仓库
- ❌ **失败恢复**：自动从备份恢复
- 📈 **变更统计**：显示插件数量变化

## 🛠️ 两个工作流对比

| 功能 | 基础版 | 增强版 |
|------|--------|--------|
| 定时运行 | ✅ | ✅ |
| 手动触发 | ✅ | ✅ |
| 错误处理 | 基本 | 高级 |
| 日志记录 | 简单 | 详细 |
| 备份恢复 | ❌ | ✅ |
| JSON验证 | ❌ | ✅ |
| 变更统计 | ❌ | ✅ |
| 强制更新 | ❌ | ✅ |

## 🔍 故障排除

### 常见问题

**权限错误**
```
Error: The process '/usr/bin/git' failed with exit code 128
```
→ 检查Actions权限设置

**Python依赖错误**
```
ModuleNotFoundError: No module named 'requests'
```
→ 检查requirements.txt文件

**网络超时**
```
请求失败: timeout
```
→ 正常现象，脚本有重试机制

### 调试步骤
1. 📋 查看Actions页面的错误日志
2. 🔧 运行本地测试：`python test_github_action.py`
3. 🚀 手动触发工作流测试
4. 📞 检查插件源URL是否可访问

## 📅 自定义运行时间

编辑 `.github/workflows/update-plugins.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 8 * * *'    # UTC 08:00 (北京时间 16:00)
  - cron: '0 0 * * 1'    # 每周一 UTC 00:00
  - cron: '0 */6 * * *'  # 每6小时运行一次
```

## 🎯 下一步

1. **立即测试**：手动运行一次工作流
2. **监控运行**：观察前几次自动运行
3. **优化配置**：根据需要调整运行频率
4. **扩展功能**：添加通知或其他自动化任务

---

🎉 **恭喜！您的自动化插件更新系统已就绪！**
