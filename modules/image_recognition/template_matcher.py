# -*- coding: utf-8 -*-
"""
模板匹配模块

提供基于OpenCV的模板匹配功能，
用于识别游戏中的卡牌和其他元素。
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from PIL import Image
import logging
import os

logger = logging.getLogger(__name__)


class TemplateMatcher:
    """
    模板匹配类
    
    使用OpenCV的模板匹配算法进行图像识别
    
    属性:
        templates (Dict[str, np.ndarray]): 模板字典
        templates_info (Dict[str, Dict]): 模板信息字典
        default_threshold (float): 默认匹配阈值
    """
    
    def __init__(self, default_threshold: float = 0.8):
        """
        初始化模板匹配器
        
        Args:
            default_threshold: 默认匹配阈值 (0.0-1.0)
        """
        self.templates: Dict[str, np.ndarray] = {}
        self.templates_info: Dict[str, Dict] = {}
        self.default_threshold = default_threshold
        
        logger.info("模板匹配器初始化完成")
    
    def load_template(self, name: str, filepath: str, 
                     category: str = "general") -> bool:
        """
        加载模板图片
        
        Args:
            name: 模板名称
            filepath: 模板文件路径
            category: 模板分类
            
        Returns:
            bool: 是否加载成功
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"模板文件不存在: {filepath}")
                return False
            
            template = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if template is None:
                logger.error(f"无法读取模板文件: {filepath}")
                return False
            
            self.templates[name] = template
            self.templates_info[name] = {
                'filepath': filepath,
                'category': category,
                'size': template.shape[:2],
                'loaded_time': __import__('time').time()
            }
            
            logger.info(f"模板加载成功: {name} ({filepath})")
            return True
            
        except Exception as e:
            logger.error(f"加载模板失败 {name}: {e}")
            return False
    
    def load_templates_from_dir(self, directory: str, 
                               category: str = "general") -> int:
        """
        从目录加载所有模板
        
        Args:
            directory: 模板目录路径
            category: 默认分类
            
        Returns:
            int: 加载成功的模板数量
        """
        if not os.path.exists(directory):
            logger.error(f"模板目录不存在: {directory}")
            return 0
        
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp')
        loaded_count = 0
        
        for filename in os.listdir(directory):
            if filename.lower().endswith(supported_formats):
                name = os.path.splitext(filename)[0]
                filepath = os.path.join(directory, filename)
                if self.load_template(name, filepath, category):
                    loaded_count += 1
        
        logger.info(f"从目录 {directory} 加载了 {loaded_count} 个模板")
        return loaded_count
    
    def remove_template(self, name: str) -> bool:
        """
        移除模板
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 是否移除成功
        """
        if name in self.templates:
            del self.templates[name]
            if name in self.templates_info:
                del self.templates_info[name]
            logger.info(f"模板已移除: {name}")
            return True
        return False
    
    def clear_templates(self) -> None:
        """清除所有模板"""
        self.templates.clear()
        self.templates_info.clear()
        logger.info("所有模板已清除")
    
    def match_template(self, source: np.ndarray, template_name: str,
                      threshold: float = None) -> List[Dict[str, Any]]:
        """
        在源图像中匹配模板
        
        Args:
            source: 源图像数组
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            List[Dict]: 匹配结果列表
        """
        if template_name not in self.templates:
            logger.warning(f"模板不存在: {template_name}")
            return []
        
        template = self.templates[template_name]
        threshold = threshold or self.default_threshold
        
        try:
            result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            matches = []
            h, w = template.shape[:2]
            
            for y, x in zip(*locations):
                match = {
                    'name': template_name,
                    'top_left': (x, y),
                    'bottom_right': (x + w, y + h),
                    'center': (x + w // 2, y + h // 2),
                    'confidence': float(result[y, x]),
                    'width': w,
                    'height': h
                }
                matches.append(match)
            
            if matches:
                logger.debug(f"模板 {template_name} 匹配到 {len(matches)} 个结果")
            
            return matches
            
        except Exception as e:
            logger.error(f"模板匹配失败: {e}")
            return []
    
    def match_all_templates(self, source: np.ndarray,
                           threshold: float = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        匹配所有模板
        
        Args:
            source: 源图像数组
            threshold: 匹配阈值
            
        Returns:
            Dict[str, List]: 各模板的匹配结果
        """
        threshold = threshold or self.default_threshold
        results = {}
        
        for template_name in self.templates:
            matches = self.match_template(source, template_name, threshold)
            if matches:
                results[template_name] = matches
        
        return results
    
    def find_best_match(self, source: np.ndarray, template_name: str,
                       threshold: float = None) -> Optional[Dict[str, Any]]:
        """
        查找最佳匹配结果
        
        Args:
            source: 源图像数组
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            Dict: 最佳匹配结果
        """
        matches = self.match_template(source, template_name, threshold)
        if matches:
            return max(matches, key=lambda x: x['confidence'])
        return None
    
    def get_template_count(self) -> int:
        """获取已加载模板数量"""
        return len(self.templates)
    
    def get_templates_by_category(self, category: str) -> List[str]:
        """
        获取指定分类的模板列表
        
        Args:
            category: 分类名称
            
        Returns:
            List[str]: 模板名称列表
        """
        return [name for name, info in self.templates_info.items() 
                if info.get('category') == category]
    
    def save_debug_image(self, source: np.ndarray, 
                        matches: List[Dict[str, Any]], 
                        output_path: str) -> bool:
        """
        保存调试图像（标注匹配结果）
        
        Args:
            source: 源图像
            matches: 匹配结果列表
            output_path: 输出文件路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            debug_image = source.copy()
            
            for match in matches:
                top_left = match['top_left']
                bottom_right = match['bottom_right']
                confidence = match['confidence']
                
                cv2.rectangle(debug_image, top_left, bottom_right, 
                             (0, 255, 0), 2)
                
                label = f"{match['name']}: {confidence:.2f}"
                cv2.putText(debug_image, label, 
                           (top_left[0], top_left[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.imwrite(output_path, debug_image)
            logger.info(f"调试图像已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存调试图像失败: {e}")
            return False
