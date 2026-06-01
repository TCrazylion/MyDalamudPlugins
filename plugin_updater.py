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
    def __init__(self, config_file: str = "origin_repo.json", output_file: str = "myrepo.json"):
        self.config_file = config_file
        self.output_file = output_file
        self.sources = []
        self.plugins = []
        self.target_plugins = {}  # plugin_name -> source_url mapping
        self.extra_fields = {}    # plugin_name -> extra fields to merge
        
    def load_config(self):
        """从JSON配置文件加载插件源和目标插件"""
        if not os.path.exists(self.config_file):
            print(f"配置文件 {self.config_file} 不存在")
            return

        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        for entry in config:
            if not entry.get('enabled', True):
                plugins_str = ', '.join(entry.get('plugins', []))
                print(f"跳过已禁用的源: {plugins_str} ({entry['source_url']})")
                continue

            source_url = entry['source_url']
            self.sources.append(source_url)

            for plugin_name in entry.get('plugins', []):
                self.target_plugins[plugin_name] = source_url
                if 'extra_fields' in entry:
                    self.extra_fields[plugin_name] = entry['extra_fields']

        print(f"加载了 {len(self.sources)} 个插件源")
        print(f"目标插件: {list(self.target_plugins.keys())}")
        
    def fetch_plugin_data(self, url: str) -> Optional[List[Dict]]:
        """从指定URL获取插件数据"""
        try:
            print(f"正在获取: {url}")
            
            # 处理GitHub链接，转换为raw链接
            if 'github.com' in url:
                if '/blob/' in url:
                    url = url.replace('github.com', 'raw.githubusercontent.com')
                    url = url.replace('/blob/', '/')
                elif '/tree/' in url:
                    url = url.replace('github.com', 'raw.githubusercontent.com')
                    url = url.replace('/tree/', '/')
                    if not url.endswith('.json'):
                        url += '/pluginmaster.json'
                
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
        
    def is_version_different(self, existing_plugin: Dict, new_plugin: Dict) -> bool:
        """比较两个插件的AssemblyVersion是否不同"""
        existing_version = existing_plugin.get('AssemblyVersion', '')
        new_version = new_plugin.get('AssemblyVersion', '')
        
        # 如果版本号为空或不存在，认为需要更新
        if not existing_version or not new_version:
            return True
            
        # 比较版本号字符串
        return existing_version != new_version
        
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
                # 合并额外字段
                if plugin_name in self.extra_fields:
                    target_plugin.update(self.extra_fields[plugin_name])
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
        """合并插件列表，根据AssemblyVersion变化决定是否更新"""
        # 创建现有插件的映射
        existing_map = {}
        for plugin in existing_plugins:
            name = plugin.get('Name') or plugin.get('InternalName')
            if name:
                existing_map[name] = plugin
                
        update_count = 0
        skip_count = 0
        
        # 添加或更新插件
        for new_plugin in new_plugins:
            name = new_plugin.get('Name') or new_plugin.get('InternalName')
            if name:
                if name in existing_map:
                    existing_plugin = existing_map[name]
                    # 检查版本是否有变化
                    if self.is_version_different(existing_plugin, new_plugin):
                        existing_map[name] = new_plugin
                        update_count += 1
                        print(f"更新插件 {name}: {existing_plugin.get('AssemblyVersion', 'unknown')} -> {new_plugin.get('AssemblyVersion', 'unknown')}")
                    else:
                        skip_count += 1
                        print(f"跳过插件 {name}: 版本无变化 ({existing_plugin.get('AssemblyVersion', 'unknown')})")
                else:
                    # 新插件，直接添加
                    existing_map[name] = new_plugin
                    update_count += 1
                    print(f"添加新插件 {name}: {new_plugin.get('AssemblyVersion', 'unknown')}")
                    
        print(f"\n插件更新统计: 更新/新增 {update_count} 个，跳过 {skip_count} 个")
        return list(existing_map.values())
        
    def save_plugins(self, plugins: List[Dict]):
        """保存插件列表到文件"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(plugins, f, ensure_ascii=False, indent=4)
            print(f"\n成功保存 {len(plugins)} 个插件到 {self.output_file}")
        except Exception as e:
            print(f"保存插件列表失败: {e}")

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

        # 加载现有插件
        existing_plugins = self.load_existing_plugins()
        print(f"现有插件数量: {len(existing_plugins)}")
        
        # 合并插件列表
        merged_plugins = self.merge_plugins(existing_plugins, new_plugins)
        
        # 保存结果
        self.save_plugins(merged_plugins)

        print("\n更新完成！")

def main():
    """主函数"""
    updater = PluginUpdater()
    updater.run()

if __name__ == "__main__":
    main()
