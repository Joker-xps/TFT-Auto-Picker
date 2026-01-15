# -*- coding: utf-8 -*-
"""
卡牌识别模块

提供游戏卡牌的识别和定位功能，
是自动拿牌系统的核心组件。
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from typing import Union
import logging
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card, CardRarity
from core.game_state import GameState, GamePhase
from modules.image_recognition.screen_capture import ScreenCapture
from modules.image_recognition.template_matcher import TemplateMatcher

logger = logging.getLogger(__name__)


class CardRecognizer:
    """
    卡牌识别类
    
    提供卡牌检测、识别和位置定位功能
    
    属性:
        screen_capture (ScreenCapture): 屏幕捕获器
        template_matcher (TemplateMatcher): 模板匹配器
        game_state (GameState): 游戏状态
        shop_regions (List[dict]): 商店区域配置
        card_templates_dir (str): 卡牌模板目录
    """
    
    DEFAULT_SHOP_REGIONS = [
        {"left": 200, "top": 500, "width": 150, "height": 200},
        {"left": 400, "top": 500, "width": 150, "height": 200},
        {"left": 600, "top": 500, "width": 150, "height": 200},
        {"left": 800, "top": 500, "width": 150, "height": 200},
        {"left": 1000, "top": 500, "width": 150, "height": 200},
    ]
    
    SHOP_AREA = {"left": 150, "top": 450, "width": 1100, "height": 300}
    
    def __init__(self, screen_capture: ScreenCapture = None,
                 card_templates_dir: str = None):
        """
        初始化卡牌识别器
        
        Args:
            screen_capture: 屏幕捕获器实例
            card_templates_dir: 卡牌模板目录
        """
        self.screen_capture = screen_capture or ScreenCapture()
        self.template_matcher = TemplateMatcher(default_threshold=0.75)
        self.game_state = GameState()
        self.shop_regions = self.DEFAULT_SHOP_REGIONS.copy()
        
        self.card_templates_dir = card_templates_dir or "resources/cards"
        self.current_season = "s13"  # 默认当前赛季
        
        from modules.config.card_config import CardConfigManager
        self.card_config = CardConfigManager()
        self._load_card_templates()
        
        logger.info("卡牌识别器初始化完成")
    
    def _load_card_templates(self) -> None:
        """
        加载卡牌模板
        
        根据当前赛季和费用分类加载模板
        """
        # 按赛季和费用分类加载模板
        for cost in range(1, 6):
            template_dir = os.path.join(self.card_templates_dir, 
                                      self.current_season, str(cost))
            if os.path.exists(template_dir):
                count = self.template_matcher.load_templates_from_dir(
                    template_dir, f"card_s{self.current_season}_c{cost}"
                )
                logger.info(f"已加载赛季 {self.current_season} 费用 {cost} 的 {count} 个卡牌模板")
        
        # 加载通用模板
        general_dir = os.path.join(self.card_templates_dir, "general")
        if os.path.exists(general_dir):
            count = self.template_matcher.load_templates_from_dir(
                general_dir, "general"
            )
            logger.info(f"已加载 {count} 个通用模板")
    
    def set_current_season(self, season: str) -> None:
        """
        设置当前赛季
        
        Args:
            season: 赛季名称
        """
        self.current_season = season
        self.card_config.set_current_season(season)
        
        # 重新加载对应赛季的模板
        self.template_matcher.clear_templates()
        self._load_card_templates()
        logger.info(f"当前赛季已切换为: {season}")
    
    def get_recognition_area(self, card_name: str) -> dict:
        """
        获取卡牌的识别区域配置
        
        Args:
            card_name: 卡牌名称
            
        Returns:
            dict: 识别区域配置 {left, top, width, height}
        """
        card_config = self.card_config.get_card(card_name)
        if card_config and 'recognition_area' in card_config:
            return card_config['recognition_area']
        
        # 默认识别区域
        return {"left": 0, "top": 0, "width": 150, "height": 200}
    
    def set_screen_capture(self, screen_capture: ScreenCapture) -> None:
        """
        设置屏幕捕获器
        
        Args:
            screen_capture: 新的屏幕捕获器
        """
        self.screen_capture = screen_capture
        logger.info("屏幕捕获器已更新")
    
    def set_shop_regions(self, regions: List[dict]) -> None:
        """
        设置商店卡槽区域
        
        Args:
            regions: 区域配置列表
        """
        self.shop_regions = regions
        logger.info(f"商店区域已更新，共 {len(regions)} 个槽位")
    
    def detect_shop_phase(self, screenshot: np.ndarray = None) -> bool:
        """
        检测是否处于商店/选牌阶段
        
        Args:
            screenshot: 可选的游戏截图
            
        Returns:
            bool: 是否处于商店阶段
        """
        if screenshot is None:
            screenshot = self.screen_capture.capture_full_screen()
        
        if screenshot.size == 0:
            logger.warning("无法获取屏幕截图")
            return False
        
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        gold_lower = np.array([20, 100, 200])
        gold_upper = np.array([40, 255, 255])
        gold_mask = cv2.inRange(hsv, gold_lower, gold_upper)
        
        gold_ratio = np.sum(gold_mask > 0) / (screenshot.shape[0] * screenshot.shape[1])
        is_shop = gold_ratio > 0.02
        
        if is_shop:
            self.game_state.set_shop_phase()
            logger.debug("检测到商店阶段")
        else:
            self.game_state.set_lobby_phase()
        
        return is_shop
    
    def recognize_cards(self, screenshot: np.ndarray = None) -> List[Card]:
        """
        识别屏幕中的卡牌
        
        Args:
            screenshot: 可选的游戏截图
            
        Returns:
            List[Card]: 识别到的卡牌列表
        """
        if screenshot is None:
            screenshot = self.screen_capture.capture_full_screen()
        
        if screenshot.size == 0:
            logger.error("无法获取屏幕截图")
            return []
        
        cards = []
        self.game_state.shop_slots = []
        
        for i, region in enumerate(self.shop_regions):
            card_image = self.screen_capture.capture_region(
                region["left"], region["top"],
                region["width"], region["height"]
            )
            
            if card_image.size == 0:
                continue
            
            card = self._recognize_single_card(card_image, i)
            if card:
                card.set_position(
                    region["left"] + region["width"] // 2,
                    region["top"] + region["height"] // 2
                )
                cards.append(card)
                self.game_state.shop_slots.append({
                    'index': i,
                    'position': (region["left"], region["top"]),
                    'has_card': True
                })
        
        self.game_state.available_cards = cards
        logger.info(f"识别到 {len(cards)} 张卡牌")
        
        return cards
    
    def _recognize_single_card(self, card_image: np.ndarray, 
                               shop_index: int) -> Optional[Card]:
        """
        识别单张卡牌
        
        Args:
            card_image: 卡牌区域图像
            shop_index: 商店槽位索引
            
        Returns:
            Card: 识别到的卡牌，如果未识别返回None
        """
        try:
            template_results = self.template_matcher.match_all_templates(
                card_image, threshold=0.7
            )
            
            best_match = None
            best_confidence = 0.7
            
            for template_name, matches in template_results.items():
                for match in matches:
                    if match['confidence'] > best_confidence:
                        best_confidence = match['confidence']
                        best_match = {
                            'name': template_name,
                            'confidence': match['confidence']
                        }
            
            if best_match:
                card = Card(
                    name=best_match['name'],
                    cost=self._estimate_cost(card_image),
                    confidence=best_match['confidence'],
                    position=None
                )
                card.shop_index = shop_index
                return card
            
            return None
            
        except Exception as e:
            logger.error(f"识别单张卡牌失败: {e}")
            return None
    
    def _estimate_cost(self, card_image: np.ndarray) -> int:
        """
        估计卡牌费用
        
        Args:
            card_image: 卡牌图像
            
        Returns:
            int: 估计的费用 (1-5)
        """
        try:
            hsv = cv2.cvtColor(card_image, cv2.COLOR_BGR2HSV)
            
            cost_ranges = {
                1: ([40, 200, 200], [50, 255, 255]),
                2: ([20, 150, 200], [30, 255, 255]),
                3: ([0, 100, 200], [10, 200, 255]),
                4: ([120, 100, 200], [140, 255, 255]),
                5: ([0, 0, 200], [180, 50, 255])
            }
            
            best_cost = 1
            max_pixels = 0
            
            for cost, (lower, upper) in cost_ranges.items():
                lower_arr = np.array(lower)
                upper_arr = np.array(upper)
                mask = cv2.inRange(hsv, lower_arr, upper_arr)
                pixel_count = np.sum(mask > 0)
                
                if pixel_count > max_pixels:
                    max_pixels = pixel_count
                    best_cost = cost
            
            return best_cost
            
        except Exception as e:
            logger.error(f"估计卡牌费用失败: {e}")
            return 1
    
    def get_card_position(self, card: Card) -> Tuple[int, int]:
        """
        获取卡牌在屏幕上的精确位置
        
        Args:
            card: 卡牌对象
            
        Returns:
            Tuple[int, int]: (x, y) 坐标
        """
        if card.position:
            return card.position
        
        if card.shop_index is not None and card.shop_index < len(self.shop_regions):
            region = self.shop_regions[card.shop_index]
            return (
                region["left"] + region["width"] // 2,
                region["top"] + region["height"] // 2
            )
        
        return (0, 0)
    
    def refresh_and_recognize(self) -> List[Card]:
        """
        刷新并重新识别卡牌
        
        Returns:
            List[Card]: 识别到的卡牌列表
        """
        self.detect_shop_phase()
        
        if self.game_state.phase == GamePhase.SHOPPING:
            return self.recognize_cards()
        
        return []
    
    def get_recognition_stats(self) -> Dict[str, Any]:
        """
        获取识别统计信息
        
        Returns:
            Dict: 统计信息字典
        """
        return {
            'total_templates': self.template_matcher.get_template_count(),
            'shop_regions_count': len(self.shop_regions),
            'recognized_cards_count': len(self.game_state.available_cards),
            'current_phase': self.game_state.phase.name,
            'is_active': self.game_state.is_active
        }
    
    def release(self) -> None:
        """释放资源"""
        self.screen_capture.release()
        logger.info("卡牌识别器资源已释放")


import os
