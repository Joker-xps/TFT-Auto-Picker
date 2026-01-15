# -*- coding: utf-8 -*-
"""
选牌策略模块

定义各种选牌策略和策略管理功能，
支持自定义优先级和多种选牌模式。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.card import Card, CardRarity
from core.game_state import GameState
import logging

logger = logging.getLogger(__name__)


class PickStrategy(ABC):
    """
    选牌策略抽象基类
    
    定义了选牌策略的接口，所有具体策略都需要实现此接口
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """获取策略名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取策略描述"""
        pass
    
    @abstractmethod
    def select_card(self, available_cards: List[Card], 
                   game_state: GameState) -> Optional[Card]:
        """
        选择最优卡牌
        
        Args:
            available_cards: 当前可选择的卡牌列表
            game_state: 当前游戏状态
            
        Returns:
            Card: 选择的卡牌，如果无合适卡牌则返回None
        """
        pass
    
    def should_pick(self, card: Card, game_state: GameState) -> bool:
        """
        检查是否应该拿取某张卡牌
        
        Args:
            card: 目标卡牌
            game_state: 当前游戏状态
            
        Returns:
            bool: 是否应该拿取
        """
        return True


class PriorityStrategy(PickStrategy):
    """
    优先级选牌策略
    
    根据预设的卡牌优先级列表进行选牌，
    优先选择优先级列表中排名靠前的卡牌
    
    属性:
        priority_list (List[str]): 卡牌优先级列表
        max_cost (int): 最高费用限制
        prefer_higher_cost (bool): 是否偏好高费卡
    """
    
    def __init__(self, priority_list: List[str] = None, max_cost: int = 5,
                 prefer_higher_cost: bool = True):
        self.priority_list = priority_list or []
        self.max_cost = max_cost
        self.prefer_higher_cost = prefer_higher_cost
        
        logger.info(f"初始化优先级策略，优先级列表长度: {len(self.priority_list)}")
    
    def get_name(self) -> str:
        return "优先级策略"
    
    def get_description(self) -> str:
        return f"根据预设优先级选牌，优先选择优先级列表中的卡牌（最高{self.max_cost}费）"
    
    def set_priority_list(self, priority_list: List[str]) -> None:
        """
        设置优先级列表
        
        Args:
            priority_list: 新的优先级列表
        """
        self.priority_list = priority_list
        logger.info(f"更新优先级列表，新长度: {len(priority_list)}")
    
    def get_priority_index(self, card_name: str) -> int:
        """
        获取卡牌在优先级列表中的索引
        
        Args:
            card_name: 卡牌名称
            
        Returns:
            int: 索引位置，未找到返回-1
        """
        try:
            return self.priority_list.index(card_name)
        except ValueError:
            return -1
    
    def select_card(self, available_cards: List[Card], 
                   game_state: GameState) -> Optional[Card]:
        if not available_cards:
            return None
        
        filtered_cards = [c for c in available_cards if c.cost <= self.max_cost]
        if not filtered_cards:
            logger.debug("没有符合条件的卡牌")
            return None
        
        scored_cards = []
        for card in filtered_cards:
            priority_index = self.get_priority_index(card.name)
            if priority_index >= 0:
                base_score = len(self.priority_list) - priority_index
                cost_bonus = card.cost * 10 if self.prefer_higher_cost else 0
                total_score = base_score + cost_bonus
                scored_cards.append((card, total_score))
        
        if scored_cards:
            scored_cards.sort(key=lambda x: x[1], reverse=True)
            selected_card = scored_cards[0][0]
            logger.info(f"选择卡牌: {selected_card.name} (分数: {scored_cards[0][1]})")
            return selected_card
        
        return None


class CostBalanceStrategy(PickStrategy):
    """
    费用平衡策略
    
    根据当前金币和等级，平衡选择各费用的卡牌
    
    属性:
        cost_weights (Dict[int, float]): 各费用的权重
    """
    
    def __init__(self, cost_weights: Dict[int, float] = None):
        self.cost_weights = cost_weights or {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0}
    
    def get_name(self) -> str:
        return "费用平衡策略"
    
    def get_description(self) -> str:
        return "根据各费用卡牌的权重进行平衡选择"
    
    def select_card(self, available_cards: List[Card],
                   game_state: GameState) -> Optional[Card]:
        if not available_cards:
            return None
        
        scored_cards = []
        for card in available_cards:
            weight = self.cost_weights.get(card.cost, 1.0)
            score = weight + card.confidence * 0.1
            scored_cards.append((card, score))
        
        if scored_cards:
            scored_cards.sort(key=lambda x: x[1], reverse=True)
            return scored_cards[0][0]
        
        return None


class CompBuildingStrategy(PickStrategy):
    """
    阵容构建策略
    
    根据预设的目标阵容需求进行选牌
    
    属性:
        target_comps (List[str]): 目标阵容需要的卡牌列表
        current_comp (List[str]): 当前已拥有的卡牌列表
    """
    
    def __init__(self, target_comp: List[str] = None):
        self.target_comp = target_comp or []
        self.current_comp: List[str] = []
    
    def get_name(self) -> str:
        return "阵容构建策略"
    
    def get_description(self) -> str:
        return f"根据目标阵容需求选牌，目标阵容: {', '.join(self.target_comp[:5])}..."
    
    def set_target_comp(self, comp: List[str]) -> None:
        """设置目标阵容"""
        self.target_comp = comp
        self.current_comp = []
    
    def select_card(self, available_cards: List[Card],
                   game_state: GameState) -> Optional[Card]:
        if not available_cards:
            return None
        
        priority_cards = [c for c in available_cards if c.name in self.target_comp]
        if priority_cards:
            return priority_cards[0]
        
        return None


class StrategyManager:
    """
    策略管理器
    
    管理多个选牌策略，支持策略切换和配置
    
    属性:
        strategies (Dict[str, PickStrategy]): 策略字典
        current_strategy (str): 当前策略名称
    """
    
    def __init__(self):
        self.strategies: Dict[str, PickStrategy] = {}
        self.current_strategy_name: Optional[str] = None
        self._register_default_strategies()
    
    def _register_default_strategies(self) -> None:
        """注册默认策略"""
        self.strategies["priority"] = PriorityStrategy()
        self.strategies["cost_balance"] = CostBalanceStrategy()
        self.strategies["comp_building"] = CompBuildingStrategy()
        self.current_strategy_name = "priority"
        logger.info("默认策略注册完成")
    
    def register_strategy(self, name: str, strategy: PickStrategy) -> bool:
        """
        注册新策略
        
        Args:
            name: 策略名称
            strategy: 策略对象
            
        Returns:
            bool: 是否注册成功
        """
        if name in self.strategies:
            logger.warning(f"策略 {name} 已存在，将被覆盖")
        self.strategies[name] = strategy
        logger.info(f"策略 {name} 注册成功")
        return True
    
    def set_strategy(self, name: str) -> bool:
        """
        设置当前策略
        
        Args:
            name: 策略名称
            
        Returns:
            bool: 是否设置成功
        """
        if name in self.strategies:
            self.current_strategy_name = name
            logger.info(f"切换策略: {name}")
            return True
        logger.error(f"策略 {name} 不存在")
        return False
    
    def get_current_strategy(self) -> Optional[PickStrategy]:
        """获取当前策略"""
        if self.current_strategy_name:
            return self.strategies.get(self.current_strategy_name)
        return None
    
    def get_available_strategies(self) -> List[str]:
        """获取所有可用策略名称"""
        return list(self.strategies.keys())
    
    def execute_selection(self, available_cards: List[Card],
                         game_state: GameState) -> Optional[Card]:
        """
        执行选牌
        
        Args:
            available_cards: 可选卡牌列表
            game_state: 游戏状态
            
        Returns:
            Card: 选择的卡牌
        """
        strategy = self.get_current_strategy()
        if strategy:
            return strategy.select_card(available_cards, game_state)
        return None
    
    def get_strategy_info(self, name: str) -> Optional[Dict[str, Any]]:
        """获取策略信息"""
        if name in self.strategies:
            strategy = self.strategies[name]
            return {
                'name': strategy.get_name(),
                'description': strategy.get_description(),
                'type': type(strategy).__name__
            }
        return None
