# -*- coding: utf-8 -*-
"""
卡牌管理界面模块

提供卡牌的添加、编辑、删除功能，以及识别区域配置
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
                              QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
                              QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
                              QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                              QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.config.card_config import CardConfigManager


class CardManagementPanel(QWidget):
    """
    卡牌管理界面组件
    
    提供卡牌的添加、编辑、删除和识别区域配置功能
    
    信号:
        card_updated: 卡牌配置更新信号
    """
    
    card_updated = pyqtSignal()
    
    def __init__(self, parent: QWidget = None):
        """
        初始化卡牌管理界面
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        self.card_config = CardConfigManager()
        self.current_season = self.card_config.get_current_season()
        
        self._setup_ui()
        self._connect_signals()
        self._load_cards()
    
    def _setup_ui(self) -> None:
        """设置UI组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 顶部控制栏
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(QLabel("当前赛季:"))
        self.season_combo = QComboBox()
        self.season_combo.addItems([f"s{i}" for i in range(1, 20)])
        self.season_combo.setCurrentText(self.current_season)
        top_layout.addWidget(self.season_combo)
        
        self.refresh_btn = QPushButton("刷新卡牌")
        top_layout.addWidget(self.refresh_btn)
        
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # 选项卡
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 卡牌列表选项卡
        self.card_list_tab = QWidget()
        self._setup_card_list_tab()
        self.tabs.addTab(self.card_list_tab, "卡牌列表")
        
        # 卡牌编辑选项卡
        self.card_edit_tab = QWidget()
        self._setup_card_edit_tab()
        self.tabs.addTab(self.card_edit_tab, "编辑卡牌")
        
        # 费用分类统计
        stats_layout = QHBoxLayout()
        for cost in range(1, 6):
            frame = QFrame()
            frame.setFrameStyle(QFrame.Box | QFrame.Raised)
            frame_layout = QVBoxLayout(frame)
            
            count = len(self.card_config.get_cards_by_cost(cost))
            frame_layout.addWidget(QLabel(f"{cost}费卡牌"))
            count_label = QLabel(f"{count}")
            count_label.setAlignment(Qt.AlignCenter)
            count_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            frame_layout.addWidget(count_label)
            
            stats_layout.addWidget(frame)
        
        main_layout.addLayout(stats_layout)
    
    def _setup_card_list_tab(self) -> None:
        """设置卡牌列表选项卡"""
        layout = QVBoxLayout(self.card_list_tab)
        
        # 费用过滤
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("费用过滤:"))
        
        self.cost_filter = QComboBox()
        self.cost_filter.addItems(["全部", "1费", "2费", "3费", "4费", "5费"])
        filter_layout.addWidget(self.cost_filter)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索卡牌...")
        filter_layout.addWidget(self.search_edit)
        
        self.search_btn = QPushButton("搜索")
        filter_layout.addWidget(self.search_btn)
        
        layout.addLayout(filter_layout)
        
        # 卡牌列表
        self.card_table = QTableWidget()
        self.card_table.setColumnCount(5)
        self.card_table.setHorizontalHeaderLabels(["卡牌名称", "费用", "赛季", "职业", "操作"])
        self.card_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.card_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.card_table)
    
    def _setup_card_edit_tab(self) -> None:
        """设置卡牌编辑选项卡"""
        layout = QVBoxLayout(self.card_edit_tab)
        
        # 卡牌基本信息
        info_group = QGroupBox("卡牌基本信息")
        info_layout = QGridLayout(info_group)
        
        info_layout.addWidget(QLabel("卡牌名称:"), 0, 0)
        self.card_name_edit = QLineEdit()
        info_layout.addWidget(self.card_name_edit, 0, 1, 1, 3)
        
        info_layout.addWidget(QLabel("费用:"), 1, 0)
        self.cost_spin = QSpinBox()
        self.cost_spin.setRange(1, 5)
        self.cost_spin.setValue(1)
        info_layout.addWidget(self.cost_spin, 1, 1)
        
        info_layout.addWidget(QLabel("赛季:"), 1, 2)
        self.edit_season_combo = QComboBox()
        self.edit_season_combo.addItems([f"s{i}" for i in range(1, 20)])
        self.edit_season_combo.setCurrentText(self.current_season)
        info_layout.addWidget(self.edit_season_combo, 1, 3)
        
        info_layout.addWidget(QLabel("职业/种族:"), 2, 0)
        self.classes_edit = QLineEdit()
        self.classes_edit.setPlaceholderText("多个职业用逗号分隔，如：挑战者,帝国")
        info_layout.addWidget(self.classes_edit, 2, 1, 1, 3)
        
        info_layout.addWidget(QLabel("模板路径:"), 3, 0)
        template_layout = QHBoxLayout()
        self.template_path_edit = QLineEdit()
        template_layout.addWidget(self.template_path_edit)
        self.browse_btn = QPushButton("浏览...")
        template_layout.addWidget(self.browse_btn)
        info_layout.addLayout(template_layout, 3, 1, 1, 3)
        
        layout.addWidget(info_group)
        
        # 识别区域配置
        area_group = QGroupBox("识别区域配置")
        area_layout = QGridLayout(area_group)
        
        area_layout.addWidget(QLabel("左上角X:"), 0, 0)
        self.area_left_spin = QSpinBox()
        self.area_left_spin.setRange(0, 4000)
        area_layout.addWidget(self.area_left_spin, 0, 1)
        
        area_layout.addWidget(QLabel("左上角Y:"), 0, 2)
        self.area_top_spin = QSpinBox()
        self.area_top_spin.setRange(0, 3000)
        area_layout.addWidget(self.area_top_spin, 0, 3)
        
        area_layout.addWidget(QLabel("右下角X:"), 1, 0)
        self.area_right_spin = QSpinBox()
        self.area_right_spin.setRange(0, 4000)
        self.area_right_spin.setValue(150)
        area_layout.addWidget(self.area_right_spin, 1, 1)
        
        area_layout.addWidget(QLabel("右下角Y:"), 1, 2)
        self.area_bottom_spin = QSpinBox()
        self.area_bottom_spin.setRange(0, 3000)
        self.area_bottom_spin.setValue(200)
        area_layout.addWidget(self.area_bottom_spin, 1, 3)
        
        area_layout.addWidget(QLabel("置信度阈值:"), 2, 0)
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(50, 100)
        self.confidence_spin.setValue(75)
        self.confidence_spin.setSuffix("%")
        area_layout.addWidget(self.confidence_spin, 2, 1)
        
        layout.addWidget(area_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.add_card_btn = QPushButton("添加卡牌")
        btn_layout.addWidget(self.add_card_btn)
        
        self.update_card_btn = QPushButton("更新卡牌")
        btn_layout.addWidget(self.update_card_btn)
        
        self.delete_card_btn = QPushButton("删除卡牌")
        btn_layout.addWidget(self.delete_card_btn)
        
        self.clear_form_btn = QPushButton("清空表单")
        btn_layout.addWidget(self.clear_form_btn)
        
        layout.addLayout(btn_layout)
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        # 顶部控制栏
        self.season_combo.currentTextChanged.connect(self._on_season_changed)
        self.refresh_btn.clicked.connect(self._load_cards)
        
        # 卡牌列表
        self.cost_filter.currentIndexChanged.connect(self._load_cards)
        self.search_btn.clicked.connect(self._load_cards)
        self.search_edit.textChanged.connect(self._load_cards)
        self.card_table.cellDoubleClicked.connect(self._on_card_double_clicked)
        
        # 卡牌编辑
        self.browse_btn.clicked.connect(self._browse_template)
        self.add_card_btn.clicked.connect(self._add_card)
        self.update_card_btn.clicked.connect(self._update_card)
        self.delete_card_btn.clicked.connect(self._delete_card)
        self.clear_form_btn.clicked.connect(self._clear_form)
    
    def _load_cards(self) -> None:
        """加载卡牌列表"""
        filter_cost = self.cost_filter.currentIndex()
        search_text = self.search_edit.text().strip().lower()
        
        # 获取卡牌数据
        if filter_cost == 0:  # 全部费用
            cards = self.card_config.get_cards_by_season(self.current_season)
        else:
            cards = self.card_config.get_cards_by_cost(filter_cost, self.current_season)
        
        # 搜索过滤
        if search_text:
            filtered_cards = {}
            for name, card in cards.items():
                if search_text in name.lower() or any(search_text in cls.lower() for cls in card['classes']):
                    filtered_cards[name] = card
            cards = filtered_cards
        
        # 填充表格
        self.card_table.setRowCount(len(cards))
        
        for row, (name, card) in enumerate(cards.items()):
            self.card_table.setItem(row, 0, QTableWidgetItem(name))
            self.card_table.setItem(row, 1, QTableWidgetItem(str(card['cost'])))
            self.card_table.setItem(row, 2, QTableWidgetItem(card['season']))
            self.card_table.setItem(row, 3, QTableWidgetItem('/'.join(card['classes'])))
            
            # 编辑按钮
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, n=name: self._edit_card(n))
            self.card_table.setCellWidget(row, 4, edit_btn)
        
        # 设置列宽
        self.card_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.card_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
    
    def _on_season_changed(self, season: str) -> None:
        """赛季变更处理"""
        self.current_season = season
        self.card_config.set_current_season(season)
        self._load_cards()
    
    def _on_card_double_clicked(self, row: int, column: int) -> None:
        """双击卡牌行处理"""
        card_name = self.card_table.item(row, 0).text()
        self._edit_card(card_name)
    
    def _browse_template(self) -> None:
        """浏览模板文件"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "选择卡牌模板图片", 
            f"resources/cards/{self.current_season}",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if filepath:
            self.template_path_edit.setText(filepath)
    
    def _add_card(self) -> None:
        """添加新卡牌"""
        name = self.card_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入卡牌名称")
            return
        
        cost = self.cost_spin.value()
        season = self.edit_season_combo.currentText()
        
        classes_text = self.classes_edit.text().strip()
        classes = [cls.strip() for cls in classes_text.split(",")] if classes_text else []
        
        template_path = self.template_path_edit.text().strip()
        
        # 计算识别区域：左边界、上边界、宽度、高度
        left = self.area_left_spin.value()
        top = self.area_top_spin.value()
        right = self.area_right_spin.value()
        bottom = self.area_bottom_spin.value()
        
        # 确保坐标有效
        left = min(left, right)
        top = min(top, bottom)
        right = max(left, right)
        bottom = max(top, bottom)
        
        width = right - left
        height = bottom - top
        
        recognition_area = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        
        confidence_threshold = self.confidence_spin.value() / 100.0  # 转换为0-1范围
        
        success = self.card_config.add_card(
            name=name,
            cost=cost,
            season=season,
            classes=classes,
            template_path=template_path,
            recognition_area=recognition_area
        )
        
        # 更新置信度阈值
        if success:
            self.card_config.update_card(name, confidence_threshold=confidence_threshold)
        
        if success:
            QMessageBox.information(self, "成功", f"卡牌 {name} 添加成功")
            self._clear_form()
            self._load_cards()
            self.card_updated.emit()
        else:
            QMessageBox.warning(self, "失败", f"卡牌 {name} 添加失败，可能已存在")
    
    def _update_card(self) -> None:
        """更新卡牌"""
        name = self.card_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入卡牌名称")
            return
        
        if not self.card_config.get_card(name):
            QMessageBox.warning(self, "警告", f"卡牌 {name} 不存在")
            return
        
        cost = self.cost_spin.value()
        season = self.edit_season_combo.currentText()
        
        classes_text = self.classes_edit.text().strip()
        classes = [cls.strip() for cls in classes_text.split(",")] if classes_text else []
        
        template_path = self.template_path_edit.text().strip()
        
        recognition_area = {
            'left': self.area_left_spin.value(),
            'top': self.area_top_spin.value(),
            'width': self.area_width_spin.value(),
            'height': self.area_height_spin.value()
        }
        
        confidence_threshold = self.confidence_spin.value() / 100.0  # 转换为0-1范围
        
        success = self.card_config.update_card(
            name=name,
            cost=cost,
            season=season,
            classes=classes,
            template_path=template_path,
            recognition_area=recognition_area,
            confidence_threshold=confidence_threshold
        )
        
        if success:
            QMessageBox.information(self, "成功", f"卡牌 {name} 更新成功")
            self._load_cards()
            self.card_updated.emit()
    
    def _delete_card(self) -> None:
        """删除卡牌"""
        name = self.card_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入要删除的卡牌名称")
            return
        
        if not self.card_config.get_card(name):
            QMessageBox.warning(self, "警告", f"卡牌 {name} 不存在")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除卡牌 {name} 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.card_config.delete_card(name)
            if success:
                QMessageBox.information(self, "成功", f"卡牌 {name} 删除成功")
                self._clear_form()
                self._load_cards()
                self.card_updated.emit()
    
    def _edit_card(self, card_name: str) -> None:
        """编辑指定卡牌"""
        card = self.card_config.get_card(card_name)
        if not card:
            return
        
        # 填充表单
        self.card_name_edit.setText(card['name'])
        self.cost_spin.setValue(card['cost'])
        self.edit_season_combo.setCurrentText(card['season'])
        self.classes_edit.setText(",".join(card['classes']))
        self.template_path_edit.setText(card['template_path'])
        
        # 识别区域 - 转换为左上角和右下角坐标
        area = card['recognition_area']
        left = area['left']
        top = area['top']
        width = area['width']
        height = area['height']
        
        right = left + width
        bottom = top + height
        
        self.area_left_spin.setValue(left)
        self.area_top_spin.setValue(top)
        self.area_right_spin.setValue(right)
        self.area_bottom_spin.setValue(bottom)
        
        # 置信度阈值
        confidence = card.get('confidence_threshold', 0.75)
        self.confidence_spin.setValue(int(confidence * 100))  # 转换为0-100范围
        
        # 切换到编辑选项卡
        self.tabs.setCurrentIndex(1)
    
    def _clear_form(self) -> None:
        """清空表单"""
        self.card_name_edit.clear()
        self.cost_spin.setValue(1)
        self.edit_season_combo.setCurrentText(self.current_season)
        self.classes_edit.clear()
        self.template_path_edit.clear()
        
        # 识别区域重置为默认值 (0,0) 到 (150,200)
        self.area_left_spin.setValue(0)
        self.area_top_spin.setValue(0)
        self.area_right_spin.setValue(150)
        self.area_bottom_spin.setValue(200)
        
        # 置信度阈值重置为默认值
        self.confidence_spin.setValue(75)
    

