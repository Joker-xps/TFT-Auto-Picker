# -*- coding: utf-8 -*-
"""
策略配置面板模块

提供选牌策略的配置和管理界面，
包括优先级列表编辑、卡组管理等。
"""

from typing import List, Optional, Dict
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QLineEdit, QPushButton, QListWidget,
                              QListWidgetItem, QComboBox, QCheckBox, QGroupBox,
                              QSpinBox, QSlider, QFileDialog, QMessageBox,
                              QFrame, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.config.card_config import CardConfigManager


class StrategyPanel(QWidget):
    """
    策略配置面板组件
    
    提供选牌策略的配置界面
    
    信号:
        strategy_changed (str): 策略变更信号
        priority_changed (List[str]): 优先级变更信号
        settings_changed (dict): 设置变更信号
    """
    
    strategy_changed = pyqtSignal(str)
    priority_changed = pyqtSignal(list)
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent: QWidget = None):
        """
        初始化策略面板
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        self.card_config = CardConfigManager()
        self.current_strategy = "priority"
        
        self._setup_ui()
        self._connect_signals()
        self._load_initial_data()
    
    def _setup_ui(self) -> None:
        """设置UI组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        strategy_group = QGroupBox("选牌策略")
        strategy_layout = QVBoxLayout(strategy_group)
        
        strategy_select_layout = QHBoxLayout()
        strategy_select_layout.addWidget(QLabel("策略:"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["优先级策略", "费用平衡策略", "阵容构建策略"])
        self.strategy_combo.setCurrentIndex(0)
        strategy_select_layout.addWidget(self.strategy_combo)
        strategy_select_layout.addStretch()
        strategy_layout.addLayout(strategy_select_layout)
        
        self.strategy_desc = QLabel("根据预设优先级选牌")
        self.strategy_desc.setStyleSheet("color: gray; font-size: 12px;")
        strategy_layout.addWidget(self.strategy_desc)
        
        main_layout.addWidget(strategy_group)
        
        priority_group = QGroupBox("卡牌优先级")
        priority_layout = QVBoxLayout(priority_group)
        
        add_layout = QHBoxLayout()
        self.card_name_edit = QLineEdit()
        self.card_name_edit.setPlaceholderText("输入卡牌名称...")
        add_layout.addWidget(self.card_name_edit)
        
        self.add_card_btn = QPushButton("添加")
        add_layout.addWidget(self.add_card_btn)
        
        self.import_btn = QPushButton("导入")
        add_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("导出")
        add_layout.addWidget(self.export_btn)
        priority_layout.addLayout(add_layout)
        
        list_layout = QHBoxLayout()
        
        self.priority_list = QListWidget()
        self.priority_list.setSelectionMode(QListWidget.ExtendedSelection)
        list_layout.addWidget(self.priority_list)
        
        button_layout = QVBoxLayout()
        self.up_btn = QPushButton("↑ 上移")
        self.down_btn = QPushButton("↓ 下移")
        self.remove_btn = QPushButton("删除")
        self.clear_btn = QPushButton("清空")
        button_layout.addWidget(self.up_btn)
        button_layout.addWidget(self.down_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        list_layout.addLayout(button_layout)
        
        priority_layout.addLayout(list_layout)
        main_layout.addWidget(priority_group)
        
        settings_group = QGroupBox("高级设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("最高费用:"), 0, 0)
        self.max_cost_spin = QSpinBox()
        self.max_cost_spin.setRange(1, 5)
        self.max_cost_spin.setValue(5)
        settings_layout.addWidget(self.max_cost_spin, 0, 1)
        
        settings_layout.addWidget(QLabel("检测间隔(秒):"), 0, 2)
        self.detect_interval_spin = QSpinBox()
        self.detect_interval_spin.setRange(1, 10)
        self.detect_interval_spin.setValue(3)
        self.detect_interval_spin.setSuffix(" ×0.1s")
        settings_layout.addWidget(self.detect_interval_spin, 0, 3)
        
        settings_layout.addWidget(QLabel("拿牌冷却(秒):"), 1, 0)
        self.cooldown_spin = QSpinBox()
        self.cooldown_spin.setRange(1, 20)
        self.cooldown_spin.setValue(5)
        self.cooldown_spin.setSuffix("  ×0.1s")
        settings_layout.addWidget(self.cooldown_spin, 1, 1)
        
        self.prefer_high_cost_check = QCheckBox("偏好高费卡")
        self.prefer_high_cost_check.setChecked(True)
        settings_layout.addWidget(self.prefer_high_cost_check, 1, 2, 1, 2)
        main_layout.addWidget(settings_group)
        
        main_layout.addStretch()
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        self.strategy_combo.currentIndexChanged.connect(self._on_strategy_changed)
        self.add_card_btn.clicked.connect(self._add_card)
        self.card_name_edit.returnPressed.connect(self._add_card)
        self.remove_btn.clicked.connect(self._remove_selected_cards)
        self.clear_btn.clicked.connect(self._clear_priority_list)
        self.up_btn.clicked.connect(self._move_up)
        self.down_btn.clicked.connect(self._move_down)
        self.import_btn.clicked.connect(self._import_priority)
        self.export_btn.clicked.connect(self._export_priority)
        
        self.max_cost_spin.valueChanged.connect(self._emit_settings_changed)
        self.detect_interval_spin.valueChanged.connect(self._emit_settings_changed)
        self.cooldown_spin.valueChanged.connect(self._emit_settings_changed)
        self.prefer_high_cost_check.toggled.connect(self._emit_settings_changed)
    
    def _load_initial_data(self) -> None:
        """加载初始数据"""
        priority_list = self.card_config.get_priority_list()
        for card in priority_list:
            self._add_card_to_list(card)
    
    def _on_strategy_changed(self, index: int) -> None:
        """策略变更处理"""
        strategies = ["priority", "cost_balance", "comp_building"]
        self.current_strategy = strategies[index]
        
        descriptions = [
            "根据预设优先级选牌，优先选择优先级列表中的卡牌",
            "根据各费用卡牌的权重进行平衡选择",
            "根据目标阵容需求选牌"
        ]
        
        self.strategy_desc.setText(descriptions[index])
        self.strategy_changed.emit(self.current_strategy)
    
    def _add_card(self) -> None:
        """添加卡牌"""
        card_name = self.card_name_edit.text().strip()
        if card_name and not self._is_card_in_list(card_name):
            self._add_card_to_list(card_name)
            self.card_name_edit.clear()
            self._save_priority_list()
            self._emit_priority_changed()
    
    def _add_card_to_list(self, card_name: str) -> None:
        """添加卡牌到列表组件"""
        item = QListWidgetItem(card_name)
        self.priority_list.addItem(item)
    
    def _is_card_in_list(self, card_name: str) -> bool:
        """检查卡牌是否已在列表中"""
        for i in range(self.priority_list.count()):
            if self.priority_list.item(i).text() == card_name:
                return True
        return False
    
    def _remove_selected_cards(self) -> None:
        """移除选中的卡牌"""
        selected_items = self.priority_list.selectedItems()
        for item in selected_items:
            self.priority_list.takeItem(self.priority_list.row(item))
        self._save_priority_list()
        self._emit_priority_changed()
    
    def _clear_priority_list(self) -> None:
        """清空优先级列表"""
        reply = QMessageBox.question(
            self, "确认", "确定清空所有优先级卡牌?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.priority_list.clear()
            self._save_priority_list()
            self._emit_priority_changed()
    
    def _move_up(self) -> None:
        """上移选中项"""
        current_row = self.priority_list.currentRow()
        if current_row > 0:
            item = self.priority_list.takeItem(current_row)
            self.priority_list.insertItem(current_row - 1, item)
            self.priority_list.setCurrentRow(current_row - 1)
            self._save_priority_list()
            self._emit_priority_changed()
    
    def _move_down(self) -> None:
        """下移选中项"""
        current_row = self.priority_list.currentRow()
        if current_row < self.priority_list.count() - 1:
            item = self.priority_list.takeItem(current_row)
            self.priority_list.insertItem(current_row + 1, item)
            self.priority_list.setCurrentRow(current_row + 1)
            self._save_priority_list()
            self._emit_priority_changed()
    
    def _import_priority(self) -> None:
        """导入优先级列表"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "导入优先级列表", "", "JSON Files (*.json)"
        )
        
        if filepath:
            if self.card_config.import_priority_list(filepath):
                self.priority_list.clear in self.card_config()
                for card in self.card_config.get_priority_list():
                    self._add_card_to_list(card)
                self._emit_priority_changed()
                QMessageBox.information(self, "成功", "优先级列表导入成功")
    
    def _export_priority(self) -> None:
        """导出优先级列表"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出优先级列表", "priority.json", "JSON Files (*.json)"
        )
        
        if filepath:
            if self.card_config.export_priority_list(filepath):
                QMessageBox.information(self, "成功", "优先级列表导出成功")
    
    def _save_priority_list(self) -> None:
        """保存优先级列表"""
        cards = []
        for i in range(self.priority_list.count()):
            cards.append(self.priority_list.item(i).text())
        self.card_config.set_priority_list(cards)
    
    def _emit_priority_changed(self) -> None:
        """发送优先级变更信号"""
        cards = []
        for i in range(self.priority_list.count()):
            cards.append(self.priority_list.item(i).text())
        self.priority_changed.emit(cards)
    
    def _emit_settings_changed(self) -> None:
        """发送设置变更信号"""
        settings = {
            'max_cost': self.max_cost_spin.value(),
            'detect_interval': self.detect_interval_spin.value() * 0.1,
            'pick_cooldown': self.cooldown_spin.value() * 0.1,
            'prefer_high_cost': self.prefer_high_cost_check.isChecked()
        }
        self.settings_changed.emit(settings)
    
    def get_priority_list(self) -> List[str]:
        """获取当前优先级列表"""
        cards = []
        for i in range(self.priority_list.count()):
            cards.append(self.priority_list.item(i).text())
        return cards
    
    def get_settings(self) -> Dict:
        """获取当前设置"""
        return {
            'max_cost': self.max_cost_spin.value(),
            'detect_interval': self.detect_interval_spin.value() * 0.1,
            'pick_cooldown': self.cooldown_spin.value() * 0.1,
            'prefer_high_cost': self.prefer_high_cost_check.isChecked(),
            'strategy': self.current_strategy
        }
    
    def set_priority_list(self, cards: List[str]) -> None:
        """设置优先级列表"""
        self.priority_list.clear()
        for card in cards:
            self._add_card_to_list(card)
        self._save_priority_list()
