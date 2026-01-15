# -*- coding: utf-8 -*-
"""
图像识别模块初始化文件
"""

from modules.image_recognition.card_recognizer import CardRecognizer
from modules.image_recognition.template_matcher import TemplateMatcher
from modules.image_recognition.screen_capture import ScreenCapture

__all__ = [
    "CardRecognizer",
    "TemplateMatcher", 
    "ScreenCapture"
]
