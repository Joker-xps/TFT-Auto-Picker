# -*- coding: utf-8 -*-
"""
模板截取工具模块

提供屏幕截图和区域选择功能，用于创建卡牌模板
"""

import cv2
import numpy as np
import os
from typing import Optional, Tuple, Dict
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QFileDialog, QMessageBox, QFrame, QApplication, 
                              QComboBox, QGridLayout, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.image_recognition.screen_capture import ScreenCapture
import pygetwindow as gw


class TemplateCaptureTool(QDialog):
    """
    模板截取工具
    
    提供屏幕截图和区域选择功能，用于创建卡牌模板
    
    信号:
        template_saved: 模板保存完成信号
    """
    
    template_saved = pyqtSignal(str, str)  # (template_path, card_name)
    
    def __init__(self, card_name: str = "", cost: int = 1, season: str = "s13", 
                 parent: QWidget = None):
        """
        初始化模板截取工具
        
        Args:
            card_name: 卡牌名称
            cost: 卡牌费用
            season: 赛季
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.card_name = card_name
        self.cost = cost
        self.season = season
        
        self.screen_capture = ScreenCapture()
        self.screenshot = None
        self.selected_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False
        
        # 游戏窗口相关
        self.game_window = None
        self.game_window_list = []
        self.auto_detect_game = True
        
        self._setup_ui()
        self._connect_signals()
        self._update_window_list()
        self._capture_screen()
    
    def _setup_ui(self) -> None:
        """设置UI组件"""
        self.setWindowTitle("模板截取工具")
        self.setModal(True)
        self.resize(1000, 750)
        
        main_layout = QVBoxLayout(self)
        
        # 顶部窗口选择区
        window_group = QGroupBox("游戏窗口选择")
        window_layout = QGridLayout(window_group)
        
        window_layout.addWidget(QLabel("游戏窗口:"), 0, 0)
        self.window_combo = QComboBox()
        window_layout.addWidget(self.window_combo, 0, 1, 1, 2)
        
        self.refresh_windows_btn = QPushButton("刷新窗口列表")
        window_layout.addWidget(self.refresh_windows_btn, 0, 3)
        
        window_layout.addWidget(QLabel("卡牌名称:"), 1, 0)
        self.card_name_label = QLabel(self.card_name)
        window_layout.addWidget(self.card_name_label, 1, 1, 1, 3)
        
        main_layout.addWidget(window_group)
        
        # 信息和控制栏
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        self.auto_detect_check = QCheckBox("自动检测游戏窗口")
        self.auto_detect_check.setChecked(True)
        control_layout.addWidget(self.auto_detect_check)
        
        self.refresh_btn = QPushButton("刷新截图")
        control_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(control_layout)
        
        # 截图显示区域
        self.screenshot_label = QLabel()
        self.screenshot_label.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.screenshot_label.setMinimumSize(800, 500)
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setMouseTracking(True)
        self.screenshot_label.setCursor(Qt.CrossCursor)
        main_layout.addWidget(self.screenshot_label)
        
        # 操作说明
        instruction_label = QLabel("操作说明: 拖动鼠标框选卡牌区域，然后点击保存模板")
        instruction_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(instruction_label)
        
        # 底部按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("保存模板")
        self.save_btn.setEnabled(False)
        btn_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("取消")
        btn_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(btn_layout)
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        # 窗口选择
        self.refresh_windows_btn.clicked.connect(self._update_window_list)
        self.window_combo.currentIndexChanged.connect(self._on_window_changed)
        self.auto_detect_check.stateChanged.connect(self._on_auto_detect_changed)
        
        # 截图控制
        self.refresh_btn.clicked.connect(self._capture_screen)
        self.save_btn.clicked.connect(self._save_template)
        self.cancel_btn.clicked.connect(self.reject)
    
    def _update_window_list(self) -> None:
        """更新游戏窗口列表"""
        try:
            windows = gw.getWindowsWithTitle('')
            game_windows = []
            
            for window in windows:
                if window.title and window.width > 500 and window.height > 300:
                    game_windows.append(window)
            
            self.game_window_list = game_windows
            
            # 更新下拉列表
            self.window_combo.clear()
            self.window_combo.addItem("自动检测游戏窗口")
            for window in game_windows:
                self.window_combo.addItem(window.title)
            
            # 自动检测金铲铲游戏窗口
            self._auto_detect_game_window()
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"获取窗口列表失败: {str(e)}")
    
    def _auto_detect_game_window(self) -> None:
        """自动检测金铲铲游戏窗口"""
        game_keywords = ["金铲铲", "TFT", "云顶之弈", "League of Legends"]
        
        for window in self.game_window_list:
            for keyword in game_keywords:
                if keyword in window.title:
                    self.game_window = window
                    # 查找对应的索引
                    for i in range(self.window_combo.count()):
                        if self.window_combo.itemText(i) == window.title:
                            self.window_combo.setCurrentIndex(i)
                            return
        
        self.game_window = None
    
    def _on_window_changed(self, index: int) -> None:
        """窗口选择变更处理"""
        if index == 0:
            self.game_window = None
            self.auto_detect_check.setChecked(True)
        else:
            self.game_window = self.game_window_list[index - 1]
            self.auto_detect_check.setChecked(False)
        
        self._capture_screen()
    
    def _on_auto_detect_changed(self, state: int) -> None:
        """自动检测选项变更处理"""
        self.auto_detect_game = (state == Qt.Checked)
        if self.auto_detect_game:
            self._auto_detect_game_window()
        self._capture_screen()
    
    def _capture_screen(self) -> None:
        """捕获游戏窗口或屏幕"""
        try:
            if self.auto_detect_game:
                self._auto_detect_game_window()
            
            if self.game_window and self.game_window.visible:
                # 捕获游戏窗口区域
                left, top, width, height = (self.game_window.left, self.game_window.top, 
                                         self.game_window.width, self.game_window.height)
                
                # 调整窗口边界，确保在屏幕范围内
                left = max(0, left)
                top = max(0, top)
                
                self.screenshot = self.screen_capture.capture_region(left, top, width, height)
                
                if self.screenshot.size == 0:
                    # 如果捕获失败，回退到全屏截图
                    self.screenshot = self.screen_capture.capture_full_screen()
            else:
                # 如果没有找到游戏窗口，回退到全屏截图
                self.screenshot = self.screen_capture.capture_full_screen()
            
            if self.screenshot.size == 0:
                QMessageBox.warning(self, "警告", "无法捕获屏幕")
                return
            
            self.selected_rect = QRect()
            self.save_btn.setEnabled(False)
            self._update_screenshot()
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"截图失败: {str(e)}")
            return
    
    def _update_screenshot(self) -> None:
        """更新截图显示"""
        if self.screenshot is None:
            return
        
        height, width, _ = self.screenshot.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.screenshot.data, width, height, bytes_per_line, QImage.Format_RGB888)
        base_pixmap = QPixmap.fromImage(q_image)
        
        # 缩放截图以适应标签
        label_size = self.screenshot_label.size()
        scaled_pixmap = base_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # 创建一个可绘制的副本
        draw_pixmap = QPixmap(scaled_pixmap)
        painter = QPainter(draw_pixmap)
        
        # 绘制选中区域
        if not self.selected_rect.isNull():
            pen = QPen(QColor(255, 0, 0), 2, Qt.DashLine)
            painter.setPen(pen)
            
            # 计算缩放比例
            scale_x = draw_pixmap.width() / width
            scale_y = draw_pixmap.height() / height
            scale = min(scale_x, scale_y)
            
            scaled_rect = QRect(
                int(self.selected_rect.x() * scale),
                int(self.selected_rect.y() * scale),
                int(self.selected_rect.width() * scale),
                int(self.selected_rect.height() * scale)
            )
            
            painter.drawRect(scaled_rect)
            
            # 绘制区域信息
            info_text = f"区域: {self.selected_rect.width()}x{self.selected_rect.height()}"
            painter.drawText(scaled_rect.topLeft() + QPoint(5, 15), info_text)
        
        painter.end()
        self.screenshot_label.setPixmap(draw_pixmap)
    
    def mousePressEvent(self, event) -> None:
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_selecting = True
            pos = self._get_screenshot_pos(event.pos())
            self.start_point = pos
            self.end_point = pos
            
    def mouseMoveEvent(self, event) -> None:
        """鼠标移动事件"""
        if self.is_selecting:
            self.end_point = self._get_screenshot_pos(event.pos())
            self.selected_rect = QRect(self.start_point, self.end_point).normalized()
            self._update_screenshot()
    
    def mouseReleaseEvent(self, event) -> None:
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.selected_rect = QRect(self.start_point, self.end_point).normalized()
            
            if not self.selected_rect.isNull() and self.selected_rect.width() > 50 and self.selected_rect.height() > 50:
                self.save_btn.setEnabled(True)
            else:
                self.save_btn.setEnabled(False)
            
            self._update_screenshot()
    
    def _get_screenshot_pos(self, frame_pos: QPoint) -> QPoint:
        """
        将窗口坐标转换为截图坐标
        
        Args:
            frame_pos: 窗口内坐标
            
        Returns:
            QPoint: 截图上的坐标
        """
        if self.screenshot is None:
            return QPoint()
        
        # 获取原始截图的实际尺寸
        height, width, _ = self.screenshot.shape
        
        # 获取QLabel的显示尺寸
        label_size = self.screenshot_label.size()
        
        # 获取显示的pixmap
        current_pixmap = self.screenshot_label.pixmap()
        if current_pixmap is None:
            return QPoint()
        
        # 获取pixmap的实际尺寸（考虑了缩放）
        pixmap_size = current_pixmap.size()
        
        # 计算实际显示的截图区域在标签中的位置（居中显示）
        x_offset = (label_size.width() - pixmap_size.width()) // 2
        y_offset = (label_size.height() - pixmap_size.height()) // 2
        
        # 计算鼠标在pixmap坐标系中的相对位置
        relative_x = frame_pos.x() - x_offset
        relative_y = frame_pos.y() - y_offset
        
        # 确保坐标在pixmap范围内
        if (relative_x < 0 or relative_x > pixmap_size.width() or 
           relative_y < 0 or relative_y > pixmap_size.height()):
            return QPoint()
        
        # 计算原始截图与显示截图的缩放比例
        scale_width = width / pixmap_size.width()
        scale_height = height / pixmap_size.height()
        
        # 将相对坐标转换为原始截图坐标
        original_x = int(relative_x * scale_width)
        original_y = int(relative_y * scale_height)
        
        # 确保坐标在原始截图范围内
        original_x = max(0, min(original_x, width - 1))
        original_y = max(0, min(original_y, height - 1))
        
        return QPoint(original_x, original_y)
    
    def _save_template(self) -> None:
        """保存模板"""
        if self.selected_rect.isNull():
            QMessageBox.warning(self, "警告", "请先选择模板区域")
            return
        
        # 创建模板保存目录
        template_dir = os.path.join("resources", "cards", self.season, str(self.cost))
        os.makedirs(template_dir, exist_ok=True)
        
        # 生成模板文件名
        template_name = self.card_name if self.card_name else "unknown_card"
        template_path = os.path.join(template_dir, f"{template_name}.png")
        
        # 裁剪选中区域
        x = self.selected_rect.x()
        y = self.selected_rect.y()
        w = self.selected_rect.width()
        h = self.selected_rect.height()
        
        template_image = self.screenshot[y:y+h, x:x+w]
        
        # 保存模板
        cv2.imwrite(template_path, template_image)
        
        QMessageBox.information(self, "成功", f"模板已保存到: {template_path}")
        
        # 发送信号
        self.template_saved.emit(template_path, self.card_name)
        self.accept()
    
    def get_selected_area(self) -> Optional[Dict[str, int]]:
        """
        获取选中区域信息
        
        Returns:
            Dict: 区域信息 {left, top, width, height}
        """
        if self.selected_rect.isNull():
            return None
        
        return {
            'left': self.selected_rect.x(),
            'top': self.selected_rect.y(),
            'width': self.selected_rect.width(),
            'height': self.selected_rect.height()
        }
    
    def get_template_path(self) -> Optional[str]:
        """
        获取模板保存路径
        
        Returns:
            str: 模板路径
        """
        if self.selected_rect.isNull():
            return None
        
        template_dir = os.path.join("resources", "cards", self.season, str(self.cost))
        template_name = self.card_name if self.card_name else "unknown_card"
        return os.path.join(template_dir, f"{template_name}.png")


def capture_template(card_name: str = "", cost: int = 1, season: str = "s13") -> Optional[str]:
    """
    捕获卡牌模板
    
    Args:
        card_name: 卡牌名称
        cost: 卡牌费用
        season: 赛季
        
    Returns:
        str: 模板路径，失败返回None
    """
    app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
    
    dialog = TemplateCaptureTool(card_name, cost, season)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_template_path()
    return None


if __name__ == "__main__":
    template_path = capture_template("测试卡牌", 3, "s13")
    print(f"模板保存到: {template_path}")
