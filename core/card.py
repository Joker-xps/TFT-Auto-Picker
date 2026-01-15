# -*- coding: utf-8 -*-
"""
卡牌数据模块

定义卡牌相关的数据结构和枚举，
包含卡牌稀有度、属性等信息。
"""

from enum import Enum, auto
from typing import Optional, List
import re


class CardRarity(Enum):
    """
    卡牌稀有度枚举
    
    定义了金铲铲之战中卡牌的稀有度等级
    """
    ONE_COST = auto()      # 1费卡
    TWO_COST = auto()      # 2费卡
    THREE_COST = auto()    # 3费卡
    FOUR_COST = auto()     # 4费卡
    FIVE_COST = auto()     # 5费卡
    SPATULA = auto()       # 特殊装备（锅铲）
    UNKNOWN = auto()       # 未知稀有度
    
    @classmethod
    def from_cost(cls, cost: int) -> 'CardRarity':
        """
        根据费用获取稀有度
        
        Args:
            cost: 卡牌费用 (1-5)
            
        Returns:
            CardRarity: 对应的稀有度
        """
        cost_map = {1: cls.ONE_COST, 2: cls.TWO_COST, 3: cls.THREE_COST, 
                   4: cls.FOUR_COST, 5: cls.FIVE_COST}
        return cost_map.get(cost, cls.UNKNOWN)
    
    @property
    def cost(self) -> int:
        """获取该稀有度对应的费用"""
        cost_map = {self.ONE_COST: 1, self.TWO_COST: 2, self.THREE_COST: 3,
                   self.FOUR_COST: 4, self.FIVE_COST: 5, self.SPATULA: 0}
        return cost_map.get(self, 0)
    
    def __str__(self) -> str:
        rarity_names = {
            self.ONE_COST: "1费", self.TWO_COST: "2费", 
            self.THREE_COST: "3费", self.FOUR_COST: "4费",
            self.FIVE_COST: "5费", self.SPATULA: "锅铲", self.UNKNOWN: "未知"
        }
        return rarity_names.get(self, "未知")


class CardClass:
    """
    卡牌职业/种族类
    
    用于表示卡牌的职业和种族信息
    """
    
    def __init__(self, name: str):
        self.name = name.strip()
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        if isinstance(other, CardClass):
            return self.name.lower() == other.name.lower()
        return False
    
    def __hash__(self) -> int:
        return hash(self.name.lower())


class Card:
    """
    卡牌数据类
    
    表示游戏中的单个卡牌信息
    
    属性:
        name (str): 卡牌名称
        cost (int): 卡牌费用
        rarity (CardRarity): 稀有度
        classes (List[CardClass]): 职业/种族列表
        template_path (str): 模板图片路径
        confidence (float): 识别置信度
        position (tuple): 在屏幕上的位置 (x, y)
        is_selected (bool): 是否已被选择
    """
    
    def __init__(self, name: str, cost: int = 1, classes: Optional[List[str]] = None,
                 template_path: str = "", confidence: float = 0.0, 
                 position: tuple = None):
        self.name = name
        self.cost = cost
        self.rarity = CardRarity.from_cost(cost)
        self.classes = [CardClass(c) for c in classes] if classes else []
        self.template_path = template_path
        self.confidence = confidence
        self.position = position or (0, 0)
        self.is_selected = False
        self.shop_index: Optional[int] = None
    
    @property
    def full_name(self) -> str:
        """获取完整的卡牌名称（包含稀有度信息）"""
        return f"[{self.rarity}] {self.name}"
    
    def set_position(self, x: int, y: int) -> None:
        """
        设置卡牌在屏幕上的位置
        
        Args:
            x: X坐标
            y: Y坐标
        """
        self.position = (x, y)
    
    def select(self) -> None:
        """标记卡牌为已选择"""
        self.is_selected = True
    
    def deselect(self) -> None:
        """标记卡牌为未选择"""
        self.is_selected = False
    
    def matches_priority(self, priorities: list) -> bool:
        """
        检查卡牌是否符合优先级列表
        
        Args:
            priorities: 优先级卡牌名称列表
            
        Returns:
            bool: 是否符合优先级
        """
        return self.name in priorities
    
    def to_dict(self) -> dict:
        """
        将卡牌信息转换为字典
        
        Returns:
            dict: 包含卡牌信息的字典
        """
        return {
            'name': self.name,
            'cost': self.cost,
            'rarity': str(self.rarity),
            'classes': [str(c) for c in self.classes],
            'confidence': self.confidence,
            'position': self.position,
            'shop_index': self.shop_index
        }
    
    def __str__(self) -> str:
        classes_str = "/".join([str(c) for c in self.classes])
        return f"{self.full_name} ({classes_str})" if classes_str else self.full_name
    
    def __repr__(self) -> str:
        return f"Card(name='{self.name}', cost={self.cost}, pos={self.position})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return self.name == other.name
        return False
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __lt__(self, other) -> bool:
        if isinstance(other, Card):
            return self.cost < other.cost
        return NotImplemented
    
    def __gt__(self, other) -> bool:
        if isinstance(other, Card):
            return self.cost > other.cost
        return NotImplemented


def parse_card_name(text: str) -> str:
    """
    解析并清理卡牌名称
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的卡牌名称
    """
    if not text:
        return ""
    
    pattern = r'[\U0001F300-\U0001F9FF\u4e00-\u9fff]+'
    matches = re.findall(pattern, text)
    return "".join(matches).strip() if matches else text.strip()
