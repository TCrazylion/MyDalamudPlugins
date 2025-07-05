#!/usr/bin/env python3
"""
测试GitHub Action配置
验证所需文件是否存在以及配置是否正确
"""

import os
import json
import yaml
from pathlib import Path

def test_github_action_setup():
    """测试GitHub Action设置"""
    print("=== GitHub Action 配置测试 ===\n")
    
    # 检查必需文件
    required_files = [
        'plugin_updater.py',
        'requirements.txt',
        'origin_repo.ini',
        '.github/workflows/update-plugins.yml'
    ]
    
    print("1. 检查必需文件:")
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} (缺失)")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ 有必需文件缺失，GitHub Action无法正常运行")
        return False
    
    # 检查YAML文件语法
    print("\n2. 检查YAML文件语法:")
    try:
        with open('.github/workflows/update-plugins.yml', 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print("   ✓ update-plugins.yml 语法正确")
    except yaml.YAMLError as e:
        print(f"   ✗ update-plugins.yml 语法错误: {e}")
        return False
    except FileNotFoundError:
        print("   ✗ update-plugins.yml 文件不存在")
        return False
    
    # 检查增强版YAML文件（如果存在）
    enhanced_yaml = '.github/workflows/update-plugins-enhanced.yml'
    if os.path.exists(enhanced_yaml):
        try:
            with open(enhanced_yaml, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print("   ✓ update-plugins-enhanced.yml 语法正确")
        except yaml.YAMLError as e:
            print(f"   ✗ update-plugins-enhanced.yml 语法错误: {e}")
            return False
    
    # 检查Python脚本语法
    print("\n3. 检查Python脚本:")
    try:
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', 'plugin_updater.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✓ plugin_updater.py 语法正确")
        else:
            print(f"   ✗ plugin_updater.py 语法错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ⚠ 无法检查Python语法: {e}")
    
    # 检查依赖文件
    print("\n4. 检查依赖配置:")
    try:
        with open('requirements.txt', 'r') as f:
            deps = f.read().strip().split('\n')
        print(f"   ✓ requirements.txt 包含 {len(deps)} 个依赖")
        for dep in deps:
            if dep.strip():
                print(f"     - {dep.strip()}")
    except Exception as e:
        print(f"   ✗ requirements.txt 读取失败: {e}")
        return False
    
    # 检查配置文件
    print("\n5. 检查插件源配置:")
    try:
        with open('origin_repo.ini', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        url_count = sum(1 for line in lines if line.strip().startswith('http'))
        plugin_count = sum(1 for line in lines if line.strip().startswith('#') and 
                          not line.strip().startswith('# 从该路径下载') and 
                          not line.strip() in ['#', '# 插件名', '# 仓库名', '# URL链接'])
        
        print(f"   ✓ origin_repo.ini 包含 {url_count} 个插件源")
        print(f"   ✓ 配置了 {plugin_count} 个插件注释")
    except Exception as e:
        print(f"   ✗ origin_repo.ini 读取失败: {e}")
        return False
    
    # 检查输出文件
    print("\n6. 检查输出文件:")
    if os.path.exists('myrepo.json'):
        try:
            with open('myrepo.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   ✓ myrepo.json 存在，包含 {len(data)} 个插件")
        except json.JSONDecodeError as e:
            print(f"   ⚠ myrepo.json JSON格式错误: {e}")
        except Exception as e:
            print(f"   ⚠ myrepo.json 读取失败: {e}")
    else:
        print("   ⚠ myrepo.json 不存在（首次运行时会创建）")
    
    print("\n✅ GitHub Action 配置检查完成！")
    print("\n下一步操作:")
    print("1. 将代码推送到GitHub仓库")
    print("2. 在仓库设置中启用Actions写入权限")
    print("3. 在Actions页面查看工作流运行情况")
    print("4. 可以手动触发工作流进行测试")
    
    return True

if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        print("需要安装PyYAML: pip install PyYAML")
        exit(1)
    
    test_github_action_setup()
