# -*- coding: utf-8 -*-
"""
游戏状态管理模块

提供游戏状态的枚举定义和状态管理功能，
用于追踪游戏的不同阶段和当前状态。
"""

from enum import Enum, auto
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GamePhase(Enum):
    """
    游戏阶段枚举
    
    定义了金铲铲之战中选牌阶段的不同状态
    """
    UNKNOWN = auto()           # 未知状态
    LOBBY = auto()             # 大厅状态
    SHOPPING = auto()          # 商店/选牌阶段
    PICKING = auto()           # 选牌中
    BATTLING = auto()          # 战斗阶段
    GAME_OVER = auto()         # 游戏结束
    PAUSED = auto()            # 暂停状态


class GameState:
    """
    游戏状态管理类
    
    用于维护和追踪当前游戏的完整状态信息
    
    属性:
        phase (GamePhase): 当前游戏阶段
        available_cards (list): 当前可选择的卡牌列表
        gold (int): 当前金币数量
        level (int): 玩家等级
        shop_slots (list): 商店槽位位置列表
        is_active (bool): 是否处于活跃选牌状态
    """
    
    def __init__(self):
        self.phase: GamePhase = GamePhase.UNKNOWN
        self.available_cards: list = []
        self.gold: int = 0
        self.level: int = 1
        self.shop_slots: list = []
        self.is_active: bool = False
        self.last_update_time: Optional[float] = None
        
        logger.info("游戏状态已初始化")
    
    def update_phase(self, new_phase: GamePhase) -> None:
        """
        更新游戏阶段
        
        Args:
            new_phase: 新的游戏阶段
        """
        if self.phase != new_phase:
            old_phase_name = self.phase.name if self.phase else "None"
            self.phase = new_phase
            self.last_update_time = __import__('time').time()
            logger.info(f"游戏阶段变更: {old_phase_name} -> {new_phase.name}")
    
    def set_shop_phase(self) -> None:
        """设置当前为商店/选牌阶段"""
        self.update_phase(GamePhase.SHOPPING)
        self.is_active = True
    
    def set_lobby_phase(self) -> None:
        """设置当前为大厅阶段"""
        self.update_phase(GamePhase.LOBBY)
        self.is_active = False
    
    def set_battle_phase(self) -> None:
        """设置当前为战斗阶段"""
        self.update_phase(GamePhase.BATTLING)
        self.is_active = False
    
    def reset(self) -> None:
        """重置游戏状态"""
        self.__init__()
        logger.info("游戏状态已重置")
    
    def to_dict(self) -> dict:
        """
        将状态转换为字典
        
        Returns:
            dict: 包含当前状态的字典
        """
        return {
            'phase': self.phase.name if self.phase else 'UNKNOWN',
            'available_cards_count': len(self.available_cards),
            'gold': self.gold,
            'level': self.level,
            'is_active': self.is_active,
            'shop_slots_count': len(self.shop_slots)
        }
    
    def __str__(self) -> str:
        return f"GameState(phase={self.phase.name}, cards={len(self.available_cards)}, gold={self.gold})"
    
    def __repr__(self) -> str:
        return self.__str__()
