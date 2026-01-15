# -*- coding: utf-8 -*-
"""
全局配置模块

管理应用程序的全局设置和配置，
支持配置文件的加载、保存和热更新。
"""

import json
import os
from typing import Any, Dict, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Settings:
    """
    全局配置管理类
    
    提供应用程序配置的加载、保存和管理功能
    
    属性:
        config_dir (Path): 配置文件目录
        config_file (Path): 配置文件路径
        _config (Dict): 配置数据字典
    """
    
    DEFAULT_CONFIG = {
        'general': {
            'language': 'zh-CN',
            'theme': 'dark',
            'start_with_windows': False,
            'minimize_to_tray': True
        },
        'automation': {
            'auto_start': False,
            'detect_interval': 0.3,
            'pick_cooldown': 0.5,
            'random_offset': True,
            'offset_range': 10,
            'double_click_mode': False
        },
        'recognition': {
            'template_threshold': 0.75,
            'auto_detect_shop': True,
            'shop_regions': [],
            'enable_debug_capture': False
        },
        'shortcuts': {
            'start_stop': 'F1',
            'pause': 'F2',
            'quick_pick': 'F3',
            'refresh': 'F5'
        },
        'ui': {
            'window_width': 1000,
            'window_height': 700,
            'log_max_lines': 1000,
            'auto_scroll_log': True,
            'show_confidence': True
        }
    }
    
    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认使用程序目录下的config
        """
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'settings.json'
        
        self._config = self.DEFAULT_CONFIG.copy()
        
        self._ensure_config_dir()
        self.load()
        
        logger.info(f"配置管理器初始化完成，配置目录: {config_dir}")
    
    def _ensure_config_dir(self) -> None:
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 是否加载成功
        """
        if not self.config_file.exists():
            logger.info("配置文件不存在，使用默认配置")
            self.save()
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self._merge_config(loaded_config)
                logger.info("配置文件加载成功")
                return True
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return False
    
    def _merge_config(self, loaded_config: dict) -> None:
        """合并配置"""
        for section, values in loaded_config.items():
            if section in self._config and isinstance(self._config[section], dict):
                self._config[section].update(values)
            else:
                self._config[section] = values
    
    def save(self) -> bool:
        """
        保存配置文件
        
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
                logger.info("配置文件保存成功")
                return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            section: 配置章节
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        try:
            return self._config[section][key]
        except KeyError:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            section: 配置章节
            key: 配置键
            value: 配置值
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
    
    def get_section(self, section: str) -> Dict:
        """
        获取整个配置章节
        
        Args:
            section: 配置章节名称
            
        Returns:
            Dict: 配置章节数据
        """
        return self._config.get(section, {})
    
    def update_section(self, section: str, values: Dict) -> None:
        """
        更新整个配置章节
        
        Args:
            section: 配置章节名称
            values: 新的配置值
        """
        self._config[section] = values
        logger.info(f"配置章节 {section} 已更新")
    
    def reset_to_default(self, section: str = None) -> None:
        """
        重置配置为默认值
        
        Args:
            section: 要重置的章节，None表示重置所有
        """
        if section:
            if section in self.DEFAULT_CONFIG:
                self._config[section] = self.DEFAULT_CONFIG[section].copy()
                logger.info(f"配置章节 {section} 已重置为默认值")
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            logger.info("所有配置已重置为默认值")
    
    def export_config(self, filepath: str) -> bool:
        """
        导出配置到文件
        
        Args:
            filepath: 导出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
                logger.info(f"配置已导出到 {filepath}")
                return True
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, filepath: str, merge: bool = True) -> bool:
        """
        从文件导入配置
        
        Args:
            filepath: 导入文件路径
            merge: 是否合并到现有配置
            
        Returns:
            bool: 是否导入成功
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            if merge:
                self._merge_config(imported_config)
            else:
                self._config = imported_config
            
            logger.info(f"配置已从 {filepath} 导入")
            return True
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False
    
    def get_all_sections(self) -> List[str]:
        """获取所有配置章节"""
        return list(self._config.keys())
    
    def register_change_callback(self, section: str, 
                                callback: callable) -> None:
        """
        注册配置变更回调
        
        Args:
            section: 配置章节
            callback: 回调函数
        """
        if not hasattr(self, '_callbacks'):
            self._callbacks = {}
        
        if section not in self._callbacks:
            self._callbacks[section] = []
        
        self._callbacks[section].append(callback)
    
    def _notify_change(self, section: str, key: str, value: Any) -> None:
        """通知配置变更"""
        if hasattr(self, '_callbacks') and section in self._callbacks:
            for callback in self._callbacks[section]:
                try:
                    callback(key, value)
                except Exception as e:
                    logger.error(f"配置回调执行失败: {e}")
