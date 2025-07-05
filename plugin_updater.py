#!/usr/bin/env python3
"""
Dalamud Plugin Repository Updater
从多个源获取指定插件信息并更新到myrepo.json
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

class PluginUpdater:
    def __init__(self, config_file: str = "origin_repo.ini", output_file: str = "myrepo.json"):
        self.config_file = config_file
        self.output_file = output_file
        self.sources = []
        self.plugins = []
        self.target_plugins = {}  # plugin_name -> source_url mapping
        self.download_tasks = []  # 特殊下载任务
        
    def load_config(self):
        """从配置文件加载插件源和目标插件"""
        if not os.path.exists(self.config_file):
            print(f"配置文件 {self.config_file} 不存在")
            return
            
        with open(self.config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_plugins = []
        current_url = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                # 处理注释行，提取插件名称
                if line.startswith('#') and line != '#':
                    comment = line[1:].strip()
                    # 如果注释包含插件名称（不是URL），则记录
                    if comment and not comment.startswith('http') and '/' not in comment:
                        # 处理多个插件名称用逗号分隔的情况
                        plugin_names = [p.strip() for p in comment.split(',')]
                        current_plugins = plugin_names
                continue
                
            # 处理下载任务注释
            if line.startswith('# 从该路径下载'):
                # 解析下载任务
                import re
                download_match = re.search(r'从该路径下载\s+(https?://[^\s]+)\s+到([^\s,，]+)目录[，,]?\s*并且重命名为\s*([^\s]+)', line)
                if download_match:
                    download_url = download_match.group(1)
                    target_dir = download_match.group(2)
                    filename = download_match.group(3)
                    self.download_tasks.append({
                        'url': download_url,
                        'dir': target_dir,
                        'filename': filename
                    })
                continue
                
            if line.startswith('http'):
                current_url = line
                self.sources.append(current_url)
                
                # 为当前URL的所有插件建立映射
                for plugin in current_plugins:
                    self.target_plugins[plugin] = current_url
                    
                current_plugins = []
                
        print(f"加载了 {len(self.sources)} 个插件源")
        print(f"目标插件: {list(self.target_plugins.keys())}")
        print(f"下载任务: {len(self.download_tasks)} 个")
        
    def fetch_plugin_data(self, url: str) -> Optional[List[Dict]]:
        """从指定URL获取插件数据"""
        try:
            print(f"正在获取: {url}")
            
            # 处理GitHub树链接
            if 'github.com' in url and '/tree/' in url:
                # 转换为raw链接
                url = url.replace('github.com', 'raw.githubusercontent.com')
                url = url.replace('/tree/', '/')
                if not url.endswith('.json'):
                    url += '/pluginmaster.json'
            
            # 处理GitHub blob链接
            elif 'github.com' in url and '/blob/' in url:
                url = url.replace('github.com', 'raw.githubusercontent.com')
                url = url.replace('/blob/', '/')
                
            # 处理releases页面
            elif 'github.com' in url and '/releases' in url:
                print(f"跳过releases页面: {url}")
                return None
                
            # 处理特殊插件页面
            elif 'aetherment.sevii.dev' in url:
                print(f"跳过特殊插件页面: {url}")
                return None
                
            # 处理特殊的plogon链接
            elif 'plogon.meowrs.com' in url:
                print(f"跳过plogon页面: {url}")
                return None
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 获取原始文本
            text_content = response.text
            
            # 尝试修复常见的JSON格式错误
            try:
                data = json.loads(text_content)
            except json.JSONDecodeError as e:
                print(f"JSON解析失败，尝试修复格式: {e}")
                # 尝试修复尾随逗号
                import re
                # 移除对象和数组中的尾随逗号
                fixed_content = re.sub(r',(\s*[}\]])', r'\1', text_content)
                try:
                    data = json.loads(fixed_content)
                    print(f"成功修复JSON格式")
                except json.JSONDecodeError as e2:
                    print(f"JSON修复失败: {e2}")
                    return None
            
            # 如果返回的是单个插件对象，转换为列表
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                print(f"未知的数据格式: {url}")
                return None
                
        except requests.RequestException as e:
            print(f"请求失败 {url}: {e}")
            return None
        except Exception as e:
            print(f"获取数据时发生错误 {url}: {e}")
            return None
            
    def find_plugin_by_name(self, plugins: List[Dict], target_name: str) -> Optional[Dict]:
        """在插件列表中查找指定名称的插件"""
        for plugin in plugins:
            if plugin.get('Name') == target_name or plugin.get('InternalName') == target_name:
                return plugin
        return None
        
    def update_plugins(self):
        """更新所有目标插件"""
        found_plugins = []
        
        # 遍历所有目标插件
        for plugin_name, source_url in self.target_plugins.items():
            print(f"\n正在查找插件: {plugin_name}")
            
            # 获取源数据
            plugin_data = self.fetch_plugin_data(source_url)
            if not plugin_data:
                continue
                
            # 查找目标插件
            target_plugin = self.find_plugin_by_name(plugin_data, plugin_name)
            if target_plugin:
                print(f"找到插件: {plugin_name}")
                found_plugins.append(target_plugin)
            else:
                print(f"未找到插件: {plugin_name}")
                
        return found_plugins
        
    def load_existing_plugins(self) -> List[Dict]:
        """加载现有的插件列表"""
        if not os.path.exists(self.output_file):
            return []
            
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载现有插件列表失败: {e}")
            return []
            
    def merge_plugins(self, existing_plugins: List[Dict], new_plugins: List[Dict]) -> List[Dict]:
        """合并插件列表，避免重复"""
        # 创建现有插件的映射
        existing_map = {}
        for plugin in existing_plugins:
            name = plugin.get('Name') or plugin.get('InternalName')
            if name:
                existing_map[name] = plugin
                
        # 添加或更新插件
        for new_plugin in new_plugins:
            name = new_plugin.get('Name') or new_plugin.get('InternalName')
            if name:
                existing_map[name] = new_plugin
                
        return list(existing_map.values())
        
    def save_plugins(self, plugins: List[Dict]):
        """保存插件列表到文件"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(plugins, f, ensure_ascii=False, indent=4)
            print(f"\n成功保存 {len(plugins)} 个插件到 {self.output_file}")
        except Exception as e:
            print(f"保存插件列表失败: {e}")
            
    def handle_download_tasks(self):
        """处理特殊的下载任务"""
        for task in self.download_tasks:
            try:
                print(f"正在下载: {task['filename']}")
                
                # 确保目标目录存在
                target_dir = task['dir']
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                # 下载文件
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(task['url'], headers=headers, timeout=30)
                response.raise_for_status()
                
                # 保存文件
                file_path = os.path.join(target_dir, task['filename'])
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                    
                print(f"成功下载: {file_path}")
                
            except Exception as e:
                print(f"下载失败 {task['filename']}: {e}")

    def run(self):
        """运行插件更新器"""
        print("=== Dalamud Plugin Repository Updater ===")
        
        # 加载配置
        self.load_config()
        if not self.target_plugins:
            print("没有找到目标插件，退出")
            return
            
        # 获取新插件数据
        new_plugins = self.update_plugins()
        print(f"\n找到 {len(new_plugins)} 个新插件")
        
        # 处理特殊下载任务
        if self.download_tasks:
            print(f"\n开始处理 {len(self.download_tasks)} 个下载任务...")
            self.handle_download_tasks()
        
        # 加载现有插件
        existing_plugins = self.load_existing_plugins()
        print(f"现有插件数量: {len(existing_plugins)}")
        
        # 合并插件列表
        merged_plugins = self.merge_plugins(existing_plugins, new_plugins)
        
        # 保存结果
        self.save_plugins(merged_plugins)
        
        # 处理特殊下载任务
        self.handle_download_tasks()
        
        print("\n更新完成！")

def main():
    """主函数"""
    updater = PluginUpdater()
    updater.run()

if __name__ == "__main__":
    main()
