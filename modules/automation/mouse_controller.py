# -*- coding: utf-8 -*-
"""
鼠标控制模块

提供模拟鼠标操作的功能，
用于自动点击和拖拽卡牌。
"""

import pyautogui
import numpy as np
from typing import Tuple, Optional, List
import time
import logging

logger = logging.getLogger(__name__)


class MouseController:
    """
    鼠标控制类
    
    提供鼠标移动、点击、拖拽等操作的模拟功能
    
    属性:
        default_delay (float): 默认操作延迟
        move_duration (float): 移动动画时间
        click_interval (float): 点击间隔
    """
    
    def __init__(self, default_delay: float = 0.05, 
                 move_duration: float = 0.1):
        """
        初始化鼠标控制器
        
        Args:
            default_delay: 默认操作延迟（秒）
            move_duration: 移动动画时间（秒）
        """
        self.default_delay = default_delay
        self.move_duration = move_duration
        self.click_interval = 0.05
        
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        logger.info("鼠标控制器初始化完成")
    
    def move_to(self, x: int, y: int, duration: float = None) -> None:
        """
        移动鼠标到指定位置
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 移动时间（秒）
        """
        duration = duration or self.move_duration
        try:
            pyautogui.moveTo(x, y, duration=duration)
            time.sleep(self.default_delay)
            logger.debug(f"鼠标移动到 ({x}, {y})")
        except Exception as e:
            logger.error(f"鼠标移动失败: {e}")
    
    def click(self, x: int = None, y: int = None, 
             button: str = 'left', clicks: int = 1) -> None:
        """
        点击鼠标
        
        Args:
            x: X坐标，如果为None则使用当前位置
            y: Y坐标
            button: 鼠标按钮 ('left', 'right', 'middle')
            clicks: 点击次数
        """
        try:
            if x is not None and y is not None:
                self.move_to(x, y)
            
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            time.sleep(self.click_interval)
            
            logger.debug(f"鼠标点击 ({x}, {y}) 按钮: {button}")
        except Exception as e:
            logger.error(f"鼠标点击失败: {e}")
    
    def double_click(self, x: int = None, y: int = None) -> None:
        """
        双击鼠标
        
        Args:
            x: X坐标
            y: Y坐标
        """
        self.click(x, y, clicks=2)
    
    def right_click(self, x: int = None, y: int = None) -> None:
        """
        右键点击
        
        Args:
            x: X坐标
            y: Y坐标
        """
        self.click(x, y, button='right')
    
    def drag(self, start_x: int, start_y: int, 
            end_x: int, end_y: int, duration: float = 0.3) -> None:
        """
        拖拽鼠标
        
        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 拖拽时间（秒）
        """
        try:
            self.move_to(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            time.sleep(self.default_delay)
            
            logger.debug(f"鼠标拖拽 ({start_x}, {start_y}) -> ({end_x}, {end_y})")
        except Exception as e:
            logger.error(f"鼠标拖拽失败: {e}")
    
    def scroll(self, clicks: int, x: int = None, y: int = None) -> None:
        """
        滚动鼠标滚轮
        
        Args:
            clicks: 滚动次数（正向上，负向下）
            x: X坐标
            y: Y坐标
        """
        try:
            pyautogui.scroll(clicks, x=x, y=y)
            time.sleep(self.default_delay)
            logger.debug(f"鼠标滚动 {clicks} 次")
        except Exception as e:
            logger.error(f"鼠标滚动失败: {e}")
    
    def get_position(self) -> Tuple[int, int]:
        """
        获取当前鼠标位置
        
        Returns:
            Tuple[int, int]: (x, y) 坐标
        """
        try:
            return pyautogui.position()
        except Exception as e:
            logger.error(f"获取鼠标位置失败: {e}")
            return (0, 0)
    
    def is_on_screen(self, x: int, y: int, 
                    tolerance: int = 10) -> bool:
        """
        检查坐标是否在屏幕范围内
        
        Args:
            x: X坐标
            y: Y坐标
            tolerance: 误差范围
            
        Returns:
            bool: 是否在屏幕范围内
        """
        screen_width, screen_height = pyautogui.size()
        return (-tolerance <= x <= screen_width + tolerance and
                -tolerance <= y <= screen_height + tolerance)
    
    def click_card(self, card_x: int, card_y: int, 
                  offset_range: int = 10) -> bool:
        """
        点击卡牌区域（带随机偏移）
        
        Args:
            card_x: 卡牌中心X坐标
            card_y: 卡牌中心Y坐标
            offset_range: 随机偏移范围
            
        Returns:
            bool: 点击是否成功
        """
        if not self.is_on_screen(card_x, card_y):
            logger.warning(f"卡牌位置超出屏幕范围: ({card_x}, {card_y})")
            return False
        
        import random
        offset_x = random.randint(-offset_range, offset_range)
        offset_y = random.randint(-offset_range, offset_range)
        
        target_x = card_x + offset_x
        target_y = card_y + offset_y
        
        self.click(target_x, target_y)
        logger.info(f"点击卡牌位置 ({target_x}, {target_y})")
        return True
    
    def rapid_click(self, x: int, y: int, 
                   count: int = 3, interval: float = 0.05) -> None:
        """
        快速连点
        
        Args:
            x: X坐标
            y: Y坐标
            count: 点击次数
            interval: 点击间隔
        """
        for i in range(count):
            self.click(x, y)
            time.sleep(interval)
        
        logger.debug(f"快速点击 {count} 次")
    
    def move_and_hold(self, x: int, y: int, 
                     duration: float = 0.5) -> None:
        """
        移动并按住
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 按住时间（秒）
        """
        try:
            self.move_to(x, y)
            pyautogui.mouseDown()
            time.sleep(duration)
            pyautogui.mouseUp()
            logger.debug(f"移动并按住 ({x}, {y}) {duration}秒")
        except Exception as e:
            logger.error(f"移动并按住失败: {e}")
    
    def execute_sequence(self, sequence: List[dict]) -> None:
        """
        执行操作序列
        
        Args:
            sequence: 操作序列，每个元素包含 'action' 和相关参数
        """
        for action in sequence:
            action_type = action.get('action', '')
            
            if action_type == 'move':
                self.move_to(action['x'], action['y'], action.get('duration'))
            elif action_type == 'click':
                self.click(action.get('x'), action.get('y'), 
                          action.get('button', 'left'))
            elif action_type == 'double_click':
                self.double_click(action.get('x'), action.get('y'))
            elif action_type == 'scroll':
                self.scroll(action.get('clicks', 0), 
                           action.get('x'), action.get('y'))
            elif action_type == 'drag':
                self.drag(action['start_x'], action['start_y'],
                         action['end_x'], action['end_y'])
            
            time.sleep(action.get('delay', self.default_delay))
        
        logger.info(f"执行操作序列完成，共 {len(sequence)} 个操作")
