# -*- coding: utf-8 -*-
"""
屏幕捕获模块

提供屏幕图像捕获功能，支持区域捕获和全屏捕获。
"""

import mss
import mss.tools
import numpy as np
from PIL import Image
from typing import Tuple, Optional, Union
import logging
import time

logger = logging.getLogger(__name__)


class ScreenCapture:
    """
    屏幕捕获类
    
    使用mss库进行高效的屏幕图像捕获
    
    属性:
        monitor (dict): 显示器配置
        screenshot_dir (str): 截图保存目录
        grab_cursor (bool): 是否捕获鼠标光标
    """
    
    def __init__(self, monitor: dict = None, screenshot_dir: str = "screenshots"):
        """
        初始化屏幕捕获器
        
        Args:
            monitor: 显示器配置，默认为主显示器
            screenshot_dir: 截图保存目录
        """
        self.screenshot_dir = screenshot_dir
        self.grab_cursor = False
        self._mss = mss.mss()  # 先初始化mss
        self.monitor = monitor or self._get_default_monitor()  # 然后获取默认显示器
        
        logger.info(f"屏幕捕获器初始化完成，分辨率: {self.monitor['width']}x{self.monitor['height']}")
    
    def _get_default_monitor(self) -> dict:
        """获取默认显示器配置"""
        # 获取实际的主显示器分辨率
        monitors = self._mss.monitors
        if len(monitors) > 1:
            # monitors[0] 是虚拟显示器，monitors[1] 是主显示器
            main_monitor = monitors[1]
            return {
                "left": main_monitor["left"],
                "top": main_monitor["top"],
                "width": main_monitor["width"],
                "height": main_monitor["height"],
                "mon": 1
            }
        
        # 回退到默认配置
        return {
            "left": 0,
            "top": 0,
            "width": 1920,
            "height": 1080,
            "mon": 1
        }
    
    def capture_full_screen(self) -> np.ndarray:
        """
        捕获整个屏幕
        
        Returns:
            np.ndarray: 屏幕图像数组 (BGR格式)
        """
        try:
            sct_img = self._mss.grab(self.monitor)
            img = np.array(sct_img)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            logger.error(f"全屏捕获失败: {e}")
            return np.array([])
    
    def capture_region(self, left: int, top: int, 
                      width: int, height: int) -> np.ndarray:
        """
        捕获屏幕指定区域
        
        Args:
            left: 区域左边界X坐标
            top: 区域上边界Y坐标
            width: 区域宽度
            height: 区域高度
            
        Returns:
            np.ndarray: 区域图像数组
        """
        region = {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }
        
        try:
            sct_img = self._mss.grab(region)
            img = np.array(sct_img)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            logger.error(f"区域捕获失败: {e}")
            return np.array([])
    
    def capture_monitor(self, monitor_index: int = 1) -> np.ndarray:
        """
        捕获指定显示器
        
        Args:
            monitor_index: 显示器索引
            
        Returns:
            np.ndarray: 显示器图像
        """
        monitors = self._mss.monitors
        
        if monitor_index >= len(monitors):
            logger.error(f"显示器 {monitor_index} 不存在")
            return np.array([])
        
        monitor = monitors[monitor_index]
        try:
            sct_img = self._mss.grab(monitor)
            img = np.array(sct_img)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            logger.error(f"显示器捕获失败: {e}")
            return np.array([])
    
    def save_screenshot(self, image: np.ndarray, filename: str = None) -> str:
        """
        保存截图到文件
        
        Args:
            image: 图像数组
            filename: 文件名，默认自动生成
            
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        filepath = f"{self.screenshot_dir}/{filename}"
        
        try:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            Image.fromarray(image).save(filepath)
            logger.info(f"截图已保存: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"截图保存失败: {e}")
            return ""
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        获取屏幕尺寸
        
        Returns:
            Tuple[int, int]: (宽度, 高度)
        """
        return (self.monitor["width"], self.monitor["height"])
    
    def get_monitor_info(self) -> dict:
        """
        获取显示器信息
        
        Returns:
            dict: 显示器配置信息
        """
        return {
            "left": self.monitor["left"],
            "top": self.monitor["top"],
            "width": self.monitor["width"],
            "height": self.monitor["height"],
            "mon": self.monitor["mon"]
        }
    
    def set_monitor(self, monitor: dict) -> None:
        """
        设置显示器配置
        
        Args:
            monitor: 新的显示器配置
        """
        self.monitor = monitor
        logger.info(f"显示器配置已更新: {monitor}")
    
    def release(self) -> None:
        """释放资源"""
        try:
            self._mss.close()
            logger.info("屏幕捕获器资源已释放")
        except Exception as e:
            logger.error(f"释放资源失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.release()
        return False


import cv2
