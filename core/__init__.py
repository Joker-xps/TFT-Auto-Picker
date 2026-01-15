# -*- coding: utf-8 -*-
"""
金铲铲之战自动拿牌系统 - TFT Auto Picker
=====================================

功能特性:
- 卡牌自动识别与抓取
- 可配置的选牌策略
- 直观的图形用户界面
- 完整的日志记录系统
- 高度模块化设计

作者: AutoDev Team
版本: 1.0.0
许可证: MIT License
"""

__version__ = "1.0.0"
__author__ = "AutoDev Team"

from core.game_state import GameState
from core.card import Card, CardRarity
from core.strategy import PickStrategy, PriorityStrategy

__all__ = [
    "GameState",
    "Card", 
    "CardRarity",
    "PickStrategy",
    "PriorityStrategy"
]
