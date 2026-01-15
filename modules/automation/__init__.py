# -*- coding: utf-8 -*-
"""
自动化模块初始化文件
"""

from modules.automation.mouse_controller import MouseController
from modules.automation.game_automator import GameAutomator

__all__ = [
    "MouseController",
    "GameAutomator"
]
