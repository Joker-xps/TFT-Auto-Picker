# -*- coding: utf-8 -*-
"""
卡牌配置模块

管理卡牌相关的配置，包括卡牌优先级列表、
卡组配置和自定义模板设置。
"""

import json
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
from core.card import Card, CardRarity
import logging

logger = logging.getLogger(__name__)


class CardConfigManager:
    """
    卡牌配置管理器
    
    管理卡牌优先级、卡组配置和自定义模板
    
    属性:
        config_dir (Path): 配置目录
        priority_file (Path): 优先级配置文件
        decks_file (Path): 卡组配置文件
        _priority_list (List[str]): 优先级列表
        _custom_decks (Dict): 自定义卡组字典
    """
    
    def __init__(self, config_dir: str = None):
        """
        初始化卡牌配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        
        self.config_dir = Path(config_dir)
        self.priority_file = self.config_dir / 'card_priority.json'
        self.decks_file = self.config_dir / 'custom_decks.json'
        self.cards_file = self.config_dir / 'cards.json'  # 新增：卡牌详细配置文件
        
        self._priority_list: List[str] = []
        self._custom_decks: Dict[str, List[str]] = {}
        self._cards: Dict[str, Dict] = {}  # 新增：卡牌详细配置
        self._current_season = "s13"  # 新增：当前赛季
        
        self._ensure_config_dir()
        self.load_configs()
        
        logger.info("卡牌配置管理器初始化完成")
    
    def _ensure_config_dir(self) -> None:
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_configs(self) -> None:
        """加载所有卡牌配置"""
        self._load_priority_list()
        self._load_custom_decks()
        self._load_cards_config()
    
    def _load_priority_list(self) -> None:
        """加载优先级列表"""
        if not self.priority_file.exists():
            self._save_default_priority_list()
            return
        
        try:
            with open(self.priority_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._priority_list = data.get('cards', [])
                logger.info(f"加载了 {len(self._priority_list)} 个优先卡牌")
        except Exception as e:
            logger.error(f"加载优先级列表失败: {e}")
    
    def _save_default_priority_list(self) -> None:
        """保存默认优先级列表"""
        default_priority = {
            'version': '1.0',
            'update_time': self._get_timestamp(),
            'cards': [
                '德莱文', '亚索', '凯尔', '霞', '洛',
                '烬', '慎', '永恩', '格温', '卡莎'
            ]
        }
        
        try:
            with open(self.priority_file, 'w', encoding='utf-8') as f:
                json.dump(default_priority, f, ensure_ascii=False, indent=4)
            self._priority_list = default_priority['cards']
            logger.info("默认优先级列表已保存")
        except Exception as e:
            logger.error(f"保存默认优先级列表失败: {e}")
    
    def _load_custom_decks(self) -> None:
        """加载自定义卡组"""
        if not self.decks_file.exists():
            self._save_default_decks()
            return
        
        try:
            with open(self.decks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._custom_decks = data.get('decks', {})
                logger.info(f"加载了 {len(self._custom_decks)} 个自定义卡组")
        except Exception as e:
            logger.error(f"加载自定义卡组失败: {e}")
    
    def _save_default_decks(self) -> None:
        """保存默认卡组"""
        default_decks = {
            'version': '1.0',
            'update_time': self._get_timestamp(),
            'decks': {
                '示例阵容': ['嘉文四世', '盖伦', '赵信', '拉克丝', '薇恩'],
                '九五至尊': ['凯尔', '瑟庄妮', '慎', '嘉文四世', '亚索']
            }
        }
        
        try:
            with open(self.decks_file, 'w', encoding='utf-8') as f:
                json.dump(default_decks, f, ensure_ascii=False, indent=4)
            self._custom_decks = default_decks['decks']
            logger.info("默认卡组已保存")
        except Exception as e:
            logger.error(f"保存默认卡组失败: {e}")
    
    def _load_cards_config(self) -> None:
        """加载卡牌详细配置"""
        if not self.cards_file.exists():
            self._save_default_cards_config()
            return
        
        try:
            with open(self.cards_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cards = data.get('cards', {})
                logger.info(f"加载了 {len(self._cards)} 张卡牌配置")
        except Exception as e:
            logger.error(f"加载卡牌配置失败: {e}")
    
    def _save_cards_config(self) -> bool:
        """保存卡牌详细配置"""
        data = {
            'version': '1.0',
            'update_time': self._get_timestamp(),
            'cards': self._cards
        }
        
        try:
            with open(self.cards_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"卡牌配置已保存，共 {len(self._cards)} 张卡牌")
            return True
        except Exception as e:
            logger.error(f"保存卡牌配置失败: {e}")
            return False
    
    def _save_default_cards_config(self) -> None:
        """保存默认卡牌配置"""
        default_cards = {
            'version': '1.0',
            'update_time': self._get_timestamp(),
            'cards': {
                '德莱文': {
                    'name': '德莱文',
                    'cost': 4,
                    'season': 's13',
                    'classes': ['挑战者', '帝国'],
                    'template_path': 'resources/cards/s13/4/draven.png',
                    'recognition_area': {'left': 0, 'top': 0, 'width': 150, 'height': 200},
                    'confidence_threshold': 0.75
                },
                '亚索': {
                    'name': '亚索',
                    'cost': 3,
                    'season': 's13',
                    'classes': ['挑战者', '浪人'],
                    'template_path': 'resources/cards/s13/3/yasuo.png',
                    'recognition_area': {'left': 0, 'top': 0, 'width': 150, 'height': 200},
                    'confidence_threshold': 0.75
                }
            }
        }
        
        try:
            with open(self.cards_file, 'w', encoding='utf-8') as f:
                json.dump(default_cards, f, ensure_ascii=False, indent=4)
            self._cards = default_cards['cards']
            logger.info("默认卡牌配置已保存")
        except Exception as e:
            logger.error(f"保存默认卡牌配置失败: {e}")
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_priority_list(self) -> List[str]:
        """
        获取优先级列表
        
        Returns:
            List[str]: 优先级卡牌名称列表
        """
        return self._priority_list.copy()
    
    def set_priority_list(self, cards: List[str]) -> None:
        """
        设置优先级列表
        
        Args:
            cards: 卡牌名称列表
        """
        self._priority_list = cards.copy()
        self._save_priority_list()
        logger.info(f"优先级列表已更新，共 {len(cards)} 个卡牌")
    
    def add_to_priority(self, card_name: str, position: int = None) -> None:
        """
        添加卡牌到优先级列表
        
        Args:
            card_name: 卡牌名称
            position: 插入位置，None表示添加到末尾
        """
        if card_name in self._priority_list:
            return
        
        if position is None or position >= len(self._priority_list):
            self._priority_list.append(card_name)
        else:
            self._priority_list.insert(position, card_name)
        
        self._save_priority_list()
    
    def remove_from_priority(self, card_name: str) -> bool:
        """
        从优先级列表移除卡牌
        
        Args:
            card_name: 卡牌名称
            
        Returns:
            bool: 是否移除成功
        """
        if card_name not in self._priority_list:
            return False
        
        self._priority_list.remove(card_name)
        self._save_priority_list()
        return True
    
    def clear_priority(self) -> None:
        """清空优先级列表"""
        self._priority_list = []
        self._save_priority_list()
        logger.info("优先级列表已清空")
    
    def _save_priority_list(self) -> None:
        """保存优先级列表到文件"""
        data = {
            'version': '1.0',
            'update_time': self._get_timestamp(),
            'cards': self._priority_list
        }
        
        try:
            with open(self.priority_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存优先级列表失败: {e}")
    
    def get_custom_decks(self) -> Dict[str, List[str]]:
        """
        获取所有自定义卡组
        
        Returns:
            Dict: 卡组名称到卡牌列表的映射
        """
        return {k: v.copy() for k, v in self._custom_decks.items()}
    
    def get_deck(self, deck_name: str) -> Optional[List[str]]:
        """
        获取指定卡组
        
        Args:
            deck_name: 卡组名称
            
        Returns:
            List[str]: 卡牌列表，不存在返回None
        """
        return self._custom_decks.get(deck_name)
    
    def save_deck(self, deck_name: str, cards: List[str]) -> bool:
        """
        保存自定义卡组
        
        Args:
            deck_name: 卡组名称
            cards: 卡牌列表
            
        Returns:
            bool: 是否保存成功
        """
        self._custom_decks[deck_name] = cards.copy()
        return self._save_custom_decks()
    
    def delete_deck(self, deck_name: str) -> bool:
        """
        删除自定义卡组
        
        Args:
            deck_name: 卡组名称
            
        Returns:
            bool: 是否删除成功
        """
        if deck_name not in self._custom_decks:
            return False
        
        del self._custom_decks[deck_name]
        return self._save_custom_decks()
    
    def rename_deck(self, old_name: str, new_name: str) -> bool:
        """
        重命名卡组
        
        Args:
            old_name: 原名称
            new_name: 新名称
            
        Returns:
            bool: 是否重命名成功
        """
        if old_name not in self._custom_decks:
            return False
        
        self._custom_decks[new_name] = self._custom_decks.pop(old_name)
        return self._save_custom_decks()
    
    def _save_custom_decks(self) -> bool:
        """保存自定义卡组到文件"""
        data = {
            'version': '1.0',
            'update_time': self._get_timestamp(),
            'decks': self._custom_decks
        }
        
        try:
            with open(self.decks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info("自定义卡组已保存")
            return True
        except Exception as e:
            logger.error(f"保存自定义卡组失败: {e}")
            return False
    
    def import_priority_list(self, filepath: str) -> bool:
        """
        导入优先级列表
        
        Args:
            filepath: 导入文件路径
            
        Returns:
            bool: 是否导入成功
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cards = data.get('cards', [])
            if isinstance(cards, list):
                self._priority_list = cards
                self._save_priority_list()
                logger.info(f"从 {filepath} 导入了 {len(cards)} 个卡牌")
                return True
            
            return False
        except Exception as e:
            logger.error(f"导入优先级列表失败: {e}")
            return False
    
    def export_priority_list(self, filepath: str) -> bool:
        """
        导出优先级列表
        
        Args:
            filepath: 导出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        data = {
            'version': '1.0',
            'export_time': self._get_timestamp(),
            'cards': self._priority_list
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"优先级列表已导出到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"导出优先级列表失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取配置统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'priority_count': len(self._priority_list),
            'custom_decks_count': len(self._custom_decks),
            'deck_names': list(self._custom_decks.keys()),
            'total_cards': len(self._cards)
        }
    
    def add_card(self, name: str, cost: int, season: str = None, 
                classes: List[str] = None, template_path: str = "",
                recognition_area: dict = None) -> bool:
        """
        添加新卡牌
        
        Args:
            name: 卡牌名称
            cost: 卡牌费用 (1-5)
            season: 所属赛季，默认使用当前赛季
            classes: 职业/种族列表
            template_path: 模板图片路径
            recognition_area: 识别区域 {left, top, width, height}
            
        Returns:
            bool: 是否添加成功
        """
        if name in self._cards:
            logger.warning(f"卡牌 {name} 已存在")
            return False
        
        season = season or self._current_season
        recognition_area = recognition_area or {'left': 0, 'top': 0, 'width': 150, 'height': 200}
        
        card_config = {
            'name': name,
            'cost': cost,
            'season': season,
            'classes': classes or [],
            'template_path': template_path,
            'recognition_area': recognition_area,
            'confidence_threshold': 0.75
        }
        
        self._cards[name] = card_config
        self._save_cards_config()
        logger.info(f"添加卡牌: {name} (费用: {cost}, 赛季: {season})")
        return True
    
    def update_card(self, name: str, **kwargs) -> bool:
        """
        更新卡牌配置
        
        Args:
            name: 卡牌名称
            kwargs: 要更新的属性
            
        Returns:
            bool: 是否更新成功
        """
        if name not in self._cards:
            logger.warning(f"卡牌 {name} 不存在")
            return False
        
        self._cards[name].update(kwargs)
        self._save_cards_config()
        logger.info(f"更新卡牌: {name}")
        return True
    
    def delete_card(self, name: str) -> bool:
        """
        删除卡牌
        
        Args:
            name: 卡牌名称
            
        Returns:
            bool: 是否删除成功
        """
        if name not in self._cards:
            return False
        
        del self._cards[name]
        self._save_cards_config()
        logger.info(f"删除卡牌: {name}")
        return True
    
    def get_card(self, name: str) -> Optional[Dict]:
        """
        获取卡牌配置
        
        Args:
            name: 卡牌名称
            
        Returns:
            Dict: 卡牌配置，不存在返回None
        """
        return self._cards.get(name)
    
    def get_all_cards(self) -> Dict[str, Dict]:
        """
        获取所有卡牌
        
        Returns:
            Dict: 所有卡牌配置
        """
        return self._cards.copy()
    
    def get_cards_by_cost(self, cost: int, season: str = None) -> Dict[str, Dict]:
        """
        按费用获取卡牌
        
        Args:
            cost: 卡牌费用 (1-5)
            season: 赛季，None表示当前赛季
            
        Returns:
            Dict: 该费用的卡牌
        """
        season = season or self._current_season
        return {name: card for name, card in self._cards.items() 
                if card['cost'] == cost and card['season'] == season}
    
    def get_cards_by_season(self, season: str) -> Dict[str, Dict]:
        """
        按赛季获取卡牌
        
        Args:
            season: 赛季
            
        Returns:
            Dict: 该赛季的卡牌
        """
        return {name: card for name, card in self._cards.items() 
                if card['season'] == season}
    
    def get_cards_by_class(self, card_class: str, season: str = None) -> Dict[str, Dict]:
        """
        按职业获取卡牌
        
        Args:
            card_class: 职业名称
            season: 赛季，None表示当前赛季
            
        Returns:
            Dict: 该职业的卡牌
        """
        season = season or self._current_season
        return {name: card for name, card in self._cards.items() 
                if card['season'] == season and card_class in card['classes']}
    
    def set_current_season(self, season: str) -> None:
        """
        设置当前赛季
        
        Args:
            season: 赛季名称
        """
        self._current_season = season
        logger.info(f"当前赛季已设置为: {season}")
    
    def get_current_season(self) -> str:
        """
        获取当前赛季
        
        Returns:
            str: 当前赛季
        """
        return self._current_season
    
    def set_card_recognition_area(self, name: str, left: int, top: int, 
                                 width: int, height: int) -> bool:
        """
        设置卡牌识别区域
        
        Args:
            name: 卡牌名称
            left: 左边界X坐标
            top: 上边界Y坐标
            width: 区域宽度
            height: 区域高度
            
        Returns:
            bool: 是否设置成功
        """
        if name not in self._cards:
            return False
        
        recognition_area = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        
        self._cards[name]['recognition_area'] = recognition_area
        self._save_cards_config()
        logger.info(f"设置卡牌 {name} 的识别区域: {recognition_area}")
        return True
    
    def get_card_template_path(self, name: str, season: str = None) -> Optional[str]:
        """
        获取卡牌模板路径
        
        Args:
            name: 卡牌名称
            season: 赛季，None表示当前赛季
            
        Returns:
            str: 模板路径，不存在返回None
        """
        card = self._cards.get(name)
        if card and (season is None or card['season'] == season):
            return card['template_path']
        return None
    
    def get_all_seasons(self) -> List[str]:
        """
        获取所有赛季
        
        Returns:
            List[str]: 赛季列表
        """
        seasons = set()
        for card in self._cards.values():
            seasons.add(card['season'])
        return sorted(list(seasons))
