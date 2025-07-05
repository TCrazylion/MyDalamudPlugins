# 🔧 GitHub Action 权限问题解决方案

## ❌ 问题描述
```
remote: Permission to TCrazylion/MyDalamudPlugins.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/TCrazylion/MyDalamudPlugins/': The requested URL returned error: 403
Error: Process completed with exit code 128.
```

## ✅ 解决方案

### 方案1: 修改仓库设置（推荐）

1. **进入仓库设置**
   - 打开您的GitHub仓库
   - 点击 **Settings** 标签

2. **配置Actions权限**
   - 在左侧菜单选择 **Actions** → **General**
   - 找到 "Workflow permissions" 部分
   - 选择 ✅ **Read and write permissions**
   - 勾选 ✅ **Allow GitHub Actions to create and approve pull requests**
   - 点击 **Save** 保存

3. **验证权限设置**
   - 确保已经选择了写入权限
   - 如果是组织仓库，可能需要组织管理员权限

### 方案2: 使用Personal Access Token（备用）

如果方案1不起作用，可以使用个人访问令牌：

1. **创建Personal Access Token**
   - 进入 GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 "Generate new token"
   - 选择权限：`repo` (Full control of private repositories)
   - 生成并复制token

2. **添加到仓库Secrets**
   - 进入仓库 Settings → Secrets and variables → Actions
   - 点击 "New repository secret"
   - Name: `PERSONAL_ACCESS_TOKEN`
   - Value: 粘贴您的token
   - 点击 "Add secret"

3. **修改工作流文件**
   ```yaml
   - name: Checkout repository
     uses: actions/checkout@v4
     with:
       token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
       fetch-depth: 0
   ```

## 🔄 已经修复的内容

我已经在两个工作流文件中添加了必要的权限配置：

```yaml
jobs:
  update-plugins:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # 允许写入仓库内容
      actions: read    # 允许读取Actions状态
```

## 🚀 测试修复

1. **推送更新后的工作流**
   ```bash
   git add .github/workflows/
   git commit -m "Fix GitHub Action permissions"
   git push
   ```

2. **手动触发测试**
   - 进入Actions页面
   - 选择 "Update Dalamud Plugins"
   - 点击 "Run workflow"

3. **检查运行结果**
   - 查看是否还有权限错误
   - 确认提交是否成功推送

## 📋 权限检查清单

- [ ] 仓库Actions权限设置为"Read and write"
- [ ] 工作流文件包含正确的permissions配置
- [ ] 如果是组织仓库，确认组织级别的Actions权限
- [ ] 检查分支保护规则是否阻止Actions推送

## 🆘 如果仍有问题

如果按照上述步骤操作后仍然有权限问题：

1. **检查分支保护规则**
   - Settings → Branches
   - 查看是否有规则阻止Actions推送

2. **使用Personal Access Token**
   - 按照方案2创建和配置PAT

3. **联系仓库管理员**
   - 如果是组织仓库，可能需要管理员协助

---

💡 **提示**: 大多数权限问题都可以通过正确配置仓库的Actions权限来解决。
