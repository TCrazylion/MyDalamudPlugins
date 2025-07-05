# GitHub Action 自动更新插件

这个GitHub Action会自动运行插件更新脚本并提交更改。

## 功能特性

- **自动运行**：每天UTC时间00:00（北京时间08:00）自动运行
- **手动触发**：支持在GitHub网页上手动触发
- **智能提交**：只有在插件信息有更新时才会提交更改
- **日志记录**：详细的运行日志和错误信息

## 设置说明

### 1. 确保仓库权限

确保GitHub Action有写入权限：
1. 进入仓库 Settings → Actions → General
2. 在 "Workflow permissions" 中选择 "Read and write permissions"
3. 勾选 "Allow GitHub Actions to create and approve pull requests"

### 2. 文件结构

确保仓库中包含以下文件：
```
.github/workflows/update-plugins.yml  # GitHub Action工作流
plugin_updater.py                     # 插件更新脚本
requirements.txt                      # Python依赖
origin_repo.ini                       # 插件源配置
myrepo.json                          # 插件仓库文件（会自动更新）
```

### 3. 运行方式

**自动运行**：
- 每天UTC时间00:00自动运行
- 如果有更新，会自动提交到仓库

**手动运行**：
1. 进入仓库的 Actions 页面
2. 选择 "Update Dalamud Plugins" 工作流
3. 点击 "Run workflow" 按钮

## 工作流程

1. **检出代码**：获取最新的仓库代码
2. **设置Python环境**：安装Python 3.11
3. **安装依赖**：安装requirements.txt中的包
4. **运行更新脚本**：执行plugin_updater.py
5. **检查更改**：检测是否有文件变化
6. **提交更改**：如果有更新，自动提交并推送

## 监控和调试

### 查看运行日志
1. 进入仓库的 Actions 页面
2. 点击具体的工作流运行
3. 查看详细的步骤日志

### 常见问题

**权限问题**：
- 确保仓库设置中已启用Actions写入权限
- 检查GITHUB_TOKEN权限

**Python依赖问题**：
- 确保requirements.txt文件存在且格式正确
- 检查Python版本兼容性

**网络问题**：
- GitHub Actions服务器可能无法访问某些插件源
- 脚本中已包含超时和重试机制

## 自定义配置

### 修改运行时间
编辑 `.github/workflows/update-plugins.yml`：
```yaml
schedule:
  - cron: '0 8 * * *'  # UTC时间08:00（北京时间16:00）
```

### 修改运行频率
```yaml
schedule:
  - cron: '0 0 * * 1'  # 每周一运行
  - cron: '0 */6 * * *'  # 每6小时运行一次
```

### 添加通知
可以添加邮件或其他通知方式：
```yaml
- name: Send notification
  if: steps.verify-changed-files.outputs.changed == 'true'
  run: |
    echo "Plugins updated successfully!"
    # 这里可以添加通知逻辑
```

## 注意事项

1. **API限制**：某些插件源可能有API请求限制
2. **网络环境**：GitHub Actions服务器网络环境可能影响某些源的访问
3. **提交频率**：如果插件源更新频繁，可能会产生大量提交
4. **文件大小**：注意myrepo.json文件大小，避免过大

## 故障排除

如果Action运行失败：
1. 检查Actions页面的错误日志
2. 确认所有配置文件都存在
3. 检查Python脚本是否有语法错误
4. 验证插件源URL是否可访问
