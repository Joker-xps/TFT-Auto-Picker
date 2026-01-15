# -*- coding: utf-8 -*-
"""
日志查看器模块

提供应用程序日志的显示和管理功能，
支持日志过滤、搜索和高亮显示。
"""

import logging
from typing import Optional, List, Callable
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QLineEdit, QPushButton, QLabel, QComboBox,
                              QFrame, QScrollBar)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QTextCursor, QFont, QColor, QTextCharFormat

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import threading


class LogHandler(logging.Handler):
    """
    日志处理器
    
    将日志记录转发到UI界面
    """
    
    def __init__(self, emit_callback):
        super().__init__()
        self.emit_callback = emit_callback
        self.setLevel(logging.DEBUG)
    
    def emit(self, record):
        try:
            msg = self.format(record)
            self.emit_callback(msg, record.levelno)
        except Exception:
            self.handleError(record)


class LogViewer(QWidget):
    """
    日志查看器组件
    
    提供日志显示、过滤和搜索功能
    
    信号:
        log_added (str, int): 日志添加信号
    """
    
    log_added = pyqtSignal(str, int)
    
    def __init__(self, parent: QWidget = None):
        """
        初始化日志查看器
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        self.max_lines = 1000
        self.auto_scroll = True
        self.log_buffer: List[tuple] = []
        
        self._setup_ui()
        self._connect_signals()
        
        self._install_log_handler()
    
    def _setup_ui(self) -> None:
        """设置UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("日志级别:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["全部", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.setCurrentIndex(1)
        filter_layout.addWidget(self.level_combo)
        
        filter_layout.addWidget(QLabel("  搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入搜索关键词...")
        self.search_edit.setMaximumWidth(200)
        filter_layout.addWidget(self.search_edit)
        
        self.clear_btn = QPushButton("清空")
        filter_layout.addWidget(self.clear_btn)
        
        self.auto_scroll_check = QPushButton("自动滚动")
        self.auto_scroll_check.setCheckable(True)
        self.auto_scroll_check.setChecked(True)
        filter_layout.addWidget(self.auto_scroll_check)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.log_text)
        
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        self.level_combo.currentIndexChanged.connect(self._filter_logs)
        self.search_edit.textChanged.connect(self._filter_logs)
        self.clear_btn.clicked.connect(self.clear_logs)
        self.auto_scroll_check.clicked.connect(self._toggle_auto_scroll)
        
        self.log_text.verticalScrollBar().valueChanged.connect(self._on_scroll)
    
    def _install_log_handler(self) -> None:
        """安装日志处理器"""
        self.log_handler = LogHandler(self._emit_log)
        logging.getLogger().addHandler(self.log_handler)
        
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self.log_handler.setFormatter(formatter)
    
    def _emit_log(self, message: str, level: int) -> None:
        """接收日志消息"""
        self.log_buffer.append((message, level))
        
        if len(self.log_buffer) > self.max_lines:
            self.log_buffer = self.log_buffer[-self.max_lines:]
        
        self.log_added.emit(message, level)
        self._update_display()
    
    def _update_display(self) -> None:
        """更新日志显示"""
        level_filter = self.level_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        filtered_logs = []
        for msg, level in self.log_buffer:
            level_name = logging.getLevelName(level)
            
            if level_filter != "全部" and level_name != level_filter:
                continue
            
            if search_text and search_text not in msg.lower():
                continue
            
            filtered_logs.append((msg, level))
        
        self._display_logs(filtered_logs)
    
    def _display_logs(self, logs: List[tuple]) -> None:
        """显示日志"""
        cursor = self.log_text.textCursor()
        was_at_bottom = (cursor.position() == len(self.log_text.toPlainText()) 
                        if self.auto_scroll else False)
        
        self.log_text.clear()
        
        for msg, level in logs:
            self._append_log_line(msg, level)
        
        if self.auto_scroll and was_at_bottom:
            self.log_text.moveCursor(QTextCursor.End)
        
        self.status_label.setText(f"显示 {len(logs)} 条日志")
    
    def _append_log_line(self, message: str, level: int) -> None:
        """添加单条日志"""
        color_map = {
            logging.DEBUG: QColor(128, 128, 128),
            logging.INFO: QColor(255, 255, 255),
            logging.WARNING: QColor(255, 200, 0),
            logging.ERROR: QColor(255, 100, 100),
            logging.CRITICAL: QColor(255, 50, 50)
        }
        
        char_format = QTextCharFormat()
        char_format.setForeground(color_map.get(level, QColor.White))
        
        self.log_text.setCurrentCharFormat(char_format)
        self.log_text.append(message)
    
    def _filter_logs(self) -> None:
        """过滤日志"""
        self._update_display()
    
    def _toggle_auto_scroll(self) -> None:
        """切换自动滚动"""
        self.auto_scroll = self.auto_scroll_check.isChecked()
    
    def _on_scroll(self, value: int) -> None:
        """滚动事件"""
        scrollbar = self.log_text.verticalScrollBar()
        if value >= scrollbar.maximum() - 10:
            self.auto_scroll_check.setChecked(True)
            self.auto_scroll = True
        else:
            self.auto_scroll_check.setChecked(False)
            self.auto_scroll = False
    
    def clear_logs(self) -> None:
        """清空日志"""
        self.log_buffer.clear()
        self.log_text.clear()
        self.status_label.setText("日志已清空")
    
    def add_log(self, message: str, level: int = logging.INFO) -> None:
        """
        手动添加日志
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        self._emit_log(message, level)
    
    def set_max_lines(self, max_lines: int) -> None:
        """
        设置最大日志行数
        
        Args:
            max_lines: 最大行数
        """
        self.max_lines = max_lines
        if len(self.log_buffer) > self.max_lines:
            self.log_buffer = self.log_buffer[-self.max_lines:]
        self._update_display()
    
    def export_logs(self, filepath: str) -> bool:
        """
        导出日志到文件
        
        Args:
            filepath: 导出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for msg, _ in self.log_buffer:
                    f.write(msg + '\n')
            return True
        except Exception as e:
            print(f"导出日志失败: {e}")
            return False
