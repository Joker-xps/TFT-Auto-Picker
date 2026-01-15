# -*- coding: utf-8 -*-
"""
游戏自动化模块

整合图像识别和鼠标控制，提供完整的游戏自动化功能，
包括自动选牌、状态监控等功能。
"""

import time
import threading
from typing import Optional, List, Callable
from enum import Enum, auto

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card
from core.game_state import GameState, GamePhase
from core.strategy import StrategyManager, PickStrategy
from modules.image_recognition.card_recognizer import CardRecognizer
from modules.automation.mouse_controller import MouseController
import logging

logger = logging.getLogger(__name__)


class AutoPickerState(Enum):
    """
    自动拿牌状态枚举
    """
    STOPPED = auto()        # 已停止
    RUNNING = auto()        # 运行中
    PAUSED = auto()         # 暂停
    DETECTING = auto()      # 检测中


class GameAutomator:
    """
    游戏自动化控制类
    
    整合卡牌识别和鼠标控制，提供完整的自动选牌功能
    
    属性:
        card_recognizer (CardRecognizer): 卡牌识别器
        mouse_controller (MouseController): 鼠标控制器
        strategy_manager (StrategyManager): 策略管理器
        game_state (GameState): 游戏状态
        auto_picker_state (AutoPickerState): 自动拿牌状态
        pick_callback (Callable): 选牌回调函数
    """
    
    DEFAULT_PICK_COOLDOWN = 0.5
    DEFAULT_DETECT_INTERVAL = 0.3
    
    def __init__(self, card_recognizer: CardRecognizer = None,
                 mouse_controller: MouseController = None):
        """
        初始化游戏自动化器
        
        Args:
            card_recognizer: 卡牌识别器实例
            mouse_controller: 鼠标控制器实例
        """
        self.card_recognizer = card_recognizer or CardRecognizer()
        self.mouse_controller = mouse_controller or MouseController()
        self.strategy_manager = StrategyManager()
        self.game_state = self.card_recognizer.game_state
        
        self.auto_picker_state = AutoPickerState.STOPPED
        self.pick_callback: Optional[Callable] = None
        
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        self.pick_cooldown = self.DEFAULT_PICK_COOLDOWN
        self.detect_interval = self.DEFAULT_DETECT_INTERVAL
        
        self.pick_count = 0
        self.total_picks = 0
        self.last_pick_time: Optional[float] = None
        
        logger.info("游戏自动化器初始化完成")
    
    def start_auto_picker(self) -> bool:
        """
        启动自动拿牌
        
        Returns:
            bool: 是否成功启动
        """
        if self.auto_picker_state == AutoPickerState.RUNNING:
            logger.warning("自动拿牌已在运行中")
            return False
        
        self._stop_event.clear()
        self._pause_event.clear()
        self.auto_picker_state = AutoPickerState.RUNNING
        
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("自动拿牌已启动")
        return True
    
    def stop_auto_picker(self) -> bool:
        """
        停止自动拿牌
        
        Returns:
            bool: 是否成功停止
        """
        if self.auto_picker_state == AutoPickerState.STOPPED:
            logger.warning("自动拿牌已停止")
            return False
        
        self._stop_event.set()
        self.auto_picker_state = AutoPickerState.STOPPED
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)
        
        logger.info("自动拿牌已停止")
        return True
    
    def pause_auto_picker(self) -> bool:
        """
        暂停自动拿牌
        
        Returns:
            bool: 是否成功暂停
        """
        if self.auto_picker_state != AutoPickerState.RUNNING:
            return False
        
        self._pause_event.set()
        self.auto_picker_state = AutoPickerState.PAUSED
        logger.info("自动拿牌已暂停")
        return True
    
    def resume_auto_picker(self) -> bool:
        """
        恢复自动拿牌
        
        Returns:
            bool: 是否成功恢复
        """
        if self.auto_picker_state != AutoPickerState.PAUSED:
            return False
        
        self._pause_event.clear()
        self.auto_picker_state = AutoPickerState.RUNNING
        logger.info("自动拿牌已恢复")
        return True
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue
            
            try:
                self._process_shop_phase()
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
            
            time.sleep(self.detect_interval)
    
    def _process_shop_phase(self) -> None:
        """处理商店阶段"""
        if not self.game_state.is_active:
            return
        
        cards = self.card_recognizer.refresh_and_recognize()
        
        if not cards:
            return
        
        selected_card = self.strategy_manager.execute_selection(
            cards, self.game_state
        )
        
        if selected_card and self._can_pick():
            self._pick_card(selected_card)
    
    def _can_pick(self) -> bool:
        """检查是否可以拿牌"""
        if self.last_pick_time is None:
            return True
        
        elapsed = time.time() - self.last_pick_time
        return elapsed >= self.pick_cooldown
    
    def _pick_card(self, card: Card) -> bool:
        """
        执行拿牌操作
        
        Args:
            card: 目标卡牌
            
        Returns:
            bool: 是否拿牌成功
        """
        position = self.card_recognizer.get_card_position(card)
        
        if not position or position == (0, 0):
            logger.warning(f"无法获取卡牌 {card.name} 的位置")
            return False
        
        success = self.mouse_controller.click_card(position[0], position[1])
        
        if success:
            card.select()
            self.pick_count += 1
            self.total_picks += 1
            self.last_pick_time = time.time()
            
            logger.info(f"成功拿取卡牌: {card.name} (第{self.pick_count}次拿牌)")
            
            if self.pick_callback:
                self.pick_callback(card)
        else:
            logger.warning(f"拿取卡牌失败: {card.name}")
        
        return success
    
    def manual_pick(self, card: Card) -> bool:
        """
        手动拿牌
        
        Args:
            card: 目标卡牌
            
        Returns:
            bool: 是否成功
        """
        return self._pick_card(card)
    
    def set_pick_callback(self, callback: Callable[[Card], None]) -> None:
        """
        设置选牌回调函数
        
        Args:
            callback: 回调函数，接收卡牌对象
        """
        self.pick_callback = callback
        logger.info("选牌回调函数已设置")
    
    def set_strategy(self, strategy_name: str) -> bool:
        """
        设置选牌策略
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            bool: 是否设置成功
        """
        return self.strategy_manager.set_strategy(strategy_name)
    
    def get_current_strategy_name(self) -> str:
        """获取当前策略名称"""
        return self.strategy_manager.current_strategy_name or ""
    
    def set_priority_list(self, priority_list: List[str]) -> None:
        """设置优先级列表"""
        strategy = self.strategy_manager.get_current_strategy()
        if strategy and hasattr(strategy, 'set_priority_list'):
            strategy.set_priority_list(priority_list)
            logger.info(f"优先级列表已更新，共 {len(priority_list)} 个卡牌")
    
    def get_statistics(self) -> dict:
        """
        获取统计数据
        
        Returns:
            dict: 统计信息
        """
        return {
            'total_picks': self.total_picks,
            'current_session_picks': self.pick_count,
            'auto_picker_state': self.auto_picker_state.name,
            'current_strategy': self.get_current_strategy_name(),
            'game_phase': self.game_state.phase.name,
            'recognized_cards': len(self.game_state.available_cards),
            'is_active': self.game_state.is_active
        }
    
    def reset_statistics(self) -> None:
        """重置统计信息"""
        self.pick_count = 0
        self.last_pick_time = None
        logger.info("统计信息已重置")
    
    def set_detect_interval(self, interval: float) -> None:
        """
        设置检测间隔
        
        Args:
            interval: 检测间隔（秒）
        """
        self.detect_interval = max(0.1, interval)
        logger.info(f"检测间隔已设置为 {self.detect_interval}秒")
    
    def set_pick_cooldown(self, cooldown: float) -> None:
        """
        设置拿牌冷却时间
        
        Args:
            cooldown: 冷却时间（秒）
        """
        self.pick_cooldown = max(0.1, cooldown)
        logger.info(f"拿牌冷却已设置为 {self.pick_cooldown}秒")
    
    def release(self) -> None:
        """释放资源"""
        self.stop_auto_picker()
        self.card_recognizer.release()
        logger.info("游戏自动化器资源已释放")
