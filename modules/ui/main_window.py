# -*- coding: utf-8 -*-
"""
主窗口模块

提供应用程序的主界面，包含所有功能组件的整合。
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QGroupBox, QSplitter, QTabWidget,
                              QFrame, QStatusBar, QToolBar, QAction, QSystemTrayIcon,
                              QMenu, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.ui.strategy_panel import StrategyPanel
from modules.ui.log_viewer import LogViewer
from modules.config.settings import Settings
from modules.automation.game_automator import GameAutomator
from modules.image_recognition.card_recognizer import CardRecognizer
from modules.automation.mouse_controller import MouseController
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    主窗口类
    
    整合所有功能组件，提供完整的用户界面
    
    信号:
        started: 启动信号
        stopped: 停止信号
        paused: 暂停信号
    """
    
    started = pyqtSignal()
    stopped = pyqtSignal()
    paused = pyqtSignal()
    
    def __init__(self):
        """
        初始化主窗口
        """
        super().__init__()
        
        self.settings = Settings()
        self.automator = None
        self._init_automator()
        
        self._setup_ui()
        self._connect_signals()
        self._apply_settings()
        
        self._setup_system_tray()
        self._setup_shortcuts()
        
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_display)
        self._update_timer.start(500)
        
        logger.info("主窗口初始化完成")
        self.show()
    
    def _init_automator(self) -> None:
        """初始化自动化器"""
        screen_capture = ScreenCapture()
        card_recognizer = CardRecognizer(screen_capture)
        mouse_controller = MouseController()
        self.automator = GameAutomator(card_recognizer, mouse_controller)
        
        self.automator.set_pick_callback(self._on_card_picked)
    
    def _setup_ui(self) -> None:
        """设置UI组件"""
        self.setWindowTitle("金铲铲之战自动拿牌工具 v1.0.0")
        self.setMinimumSize(1000, 700)
        
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
    
    def _create_toolbar(self) -> None:
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        start_icon = QIcon.fromTheme("media-playback-start")
        stop_icon = QIcon.fromTheme("media-playback-stop")
        pause_icon = QIcon.fromTheme("media-playback-pause")
        
        self.start_action = QAction(start_icon, "启动 (F1)", self)
        self.start_action.triggered.connect(self._toggle_auto_picker)
        toolbar.addAction(self.start_action)
        
        self.pause_action = QAction(pause_icon, "暂停 (F2)", self)
        self.pause_action.triggered.connect(self._toggle_pause)
        self.pause_action.setEnabled(False)
        toolbar.addAction(self.pause_action)
        
        toolbar.addSeparator()
        
        refresh_icon = QIcon.fromTheme("view-refresh")
        refresh_action = QAction(refresh_icon, "刷新识别 (F5)", self)
        refresh_action.triggered.connect(self._refresh_recognition)
        toolbar.addAction(refresh_action)
    
    def _create_central_widget(self) -> None:
        """创建中心组件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 选项卡式设计
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建主选项卡
        self.main_tabs = QTabWidget()
        main_layout.addWidget(self.main_tabs)
        
        # 自动拿牌选项卡
        self.auto_picker_tab = QWidget()
        self._setup_auto_picker_tab()
        self.main_tabs.addTab(self.auto_picker_tab, "自动拿牌")
        
        # 卡牌管理选项卡
        from modules.ui.card_management_panel import CardManagementPanel
        self.card_management_tab = CardManagementPanel()
        self.main_tabs.addTab(self.card_management_tab, "卡牌管理")
        
        # 日志选项卡
        self.log_tab = QWidget()
        self._setup_log_tab()
        self.main_tabs.addTab(self.log_tab, "运行日志")
    
    def _setup_auto_picker_tab(self) -> None:
        """设置自动拿牌选项卡"""
        layout = QHBoxLayout(self.auto_picker_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self._create_status_panel(left_layout)
        self._create_card_preview_panel(left_layout)
        left_panel.setLayout(left_layout)
        
        layout.addWidget(left_panel, stretch=1)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.strategy_panel = StrategyPanel()
        right_layout.addWidget(self.strategy_panel)
        
        layout.addWidget(right_panel, stretch=2)
    
    def _setup_log_tab(self) -> None:
        """设置日志选项卡"""
        layout = QVBoxLayout(self.log_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.log_viewer = LogViewer()
        layout.addWidget(self.log_viewer)
    
    def _create_status_panel(self, parent_layout: QVBoxLayout) -> None:
        """创建状态面板"""
        status_group = QGroupBox("运行状态")
        status_layout = QGridLayout()
        
        status_layout.addWidget(QLabel("自动拿牌:"), 0, 0)
        self.status_label = QLabel("已停止")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        status_layout.addWidget(self.status_label, 0, 1)
        
        status_layout.addWidget(QLabel("游戏阶段:"), 1, 0)
        self.phase_label = QLabel("未知")
        status_layout.addWidget(self.phase_label, 1, 1)
        
        status_layout.addWidget(QLabel("识别卡牌:"), 2, 0)
        self.card_count_label = QLabel("0")
        status_layout.addWidget(self.card_count_label, 2, 1)
        
        status_layout.addWidget(QLabel("已拿卡牌:"), 3, 0)
        self.pick_count_label = QLabel("0")
        status_layout.addWidget(self.pick_count_label, 3, 1)
        
        status_layout.addWidget(QLabel("当前策略:"), 4, 0)
        self.strategy_label = QLabel("优先级策略")
        status_layout.addWidget(self.strategy_label, 4, 1)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("启动")
        self.start_btn.clicked.connect(self._toggle_auto_picker)
        button_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.clicked.connect(self._toggle_pause)
        self.pause_btn.setEnabled(False)
        button_layout.addWidget(self.pause_btn)
        
        status_layout.addLayout(button_layout, 5, 0, 1, 2)
        
        status_group.setLayout(status_layout)
        parent_layout.addWidget(status_group)
    
    def _create_card_preview_panel(self, parent_layout: QVBoxLayout) -> None:
        """创建卡牌预览面板"""
        preview_group = QGroupBox("当前识别到的卡牌")
        preview_layout = QVBoxLayout()
        
        self.card_preview = QLabel("暂无卡牌")
        self.card_preview.setAlignment(Qt.AlignCenter)
        self.card_preview.setMinimumHeight(150)
        self.card_preview.setStyleSheet("""
            background-color: #2a2a2a;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        """)
        preview_layout.addWidget(self.card_preview)
        
        preview_group.setLayout(preview_layout)
        parent_layout.addWidget(preview_group)
    
    def _create_status_bar(self) -> None:
        """创建状态栏"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("准备就绪")
    
    def _connect_signals(self) -> None:
        """连接信号和槽"""
        self.strategy_panel.strategy_changed.connect(self._on_strategy_changed)
        self.strategy_panel.priority_changed.connect(self._on_priority_changed)
        self.strategy_panel.settings_changed.connect(self._on_settings_changed)
    
    def _apply_settings(self) -> None:
        """应用设置"""
        width = self.settings.get('ui', 'window_width', 1000)
        height = self.settings.get('ui', 'window_height', 700)
        self.resize(width, height)
    
    def _setup_system_tray(self) -> None:
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("金铲铲之战自动拿牌工具")
        
        tray_menu = QMenu()
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        toggle_action = QAction("启动/停止", self)
        toggle_action.triggered.connect(self._toggle_auto_picker)
        tray_menu.addAction(toggle_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _setup_shortcuts(self) -> None:
        """设置快捷键"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        QShortcut(QKeySequence("F1"), self, self._toggle_auto_picker)
        QShortcut(QKeySequence("F2"), self, self._toggle_pause)
        QShortcut(QKeySequence("F5"), self, self._refresh_recognition)
        QShortcut(QKeySequence("Esc"), self, self._toggle_auto_picker)
    
    def _toggle_auto_picker(self) -> None:
        """切换自动拿牌状态"""
        if self.automator.auto_picker_state.name == 'STOPPED':
            self._start_auto_picker()
        else:
            self._stop_auto_picker()
    
    def _start_auto_picker(self) -> None:
        """启动自动拿牌"""
        if self.automator.start_auto_picker():
            self.start_action.setText("停止 (F1)")
            self.pause_action.setEnabled(True)
            self.start_btn.setText("停止")
            self.pause_btn.setEnabled(True)
            
            self.status_label.setText("运行中")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
            self.statusBar.showMessage("自动拿牌已启动")
            
            self.started.emit()
            logger.info("自动拿牌已启动")
    
    def _stop_auto_picker(self) -> None:
        """停止自动拿牌"""
        if self.automator.stop_auto_picker():
            self.start_action.setText("启动 (F1)")
            self.pause_action.setEnabled(False)
            self.start_btn.setText("启动")
            self.pause_btn.setText("暂停")
            self.pause_btn.setEnabled(False)
            
            self.status_label.setText("已停止")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
            self.statusBar.showMessage("自动拿牌已停止")
            
            self.stopped.emit()
            logger.info("自动拿牌已停止")
    
    def _toggle_pause(self) -> None:
        """切换暂停状态"""
        if self.automator.auto_picker_state.name == 'RUNNING':
            self.automator.pause_auto_picker()
            self.pause_action.setText("继续 (F2)")
            self.pause_btn.setText("继续")
            self.status_label.setText("已暂停")
            self.status_label.setStyleSheet("font-weight: bold; color: yellow;")
            self.paused.emit()
        elif self.automator.auto_picker_state.name == 'PAUSED':
            self.automator.resume_auto_picker()
            self.pause_action.setText("暂停 (F2)")
            self.pause_btn.setText("暂停")
            self.status_label.setText("运行中")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
    
    def _refresh_recognition(self) -> None:
        """刷新识别"""
        cards = self.automator.card_recognizer.refresh_and_recognize()
        self._update_card_display(cards)
        self.statusBar.showMessage(f"已刷新，识别到 {len(cards)} 张卡牌")
    
    def _on_card_picked(self, card) -> None:
        """卡牌拿取回调"""
        self.log_viewer.add_log(f"成功拿取: {card.name}", 20)
    
    def _on_strategy_changed(self, strategy: str) -> None:
        """策略变更处理"""
        self.automator.set_strategy(strategy)
        
        strategy_names = {
            'priority': '优先级策略',
            'cost_balance': '费用平衡策略',
            'comp_building': '阵容构建策略'
        }
        
        self.strategy_label.setText(strategy_names.get(strategy, strategy))
        self.log_viewer.add_log(f"策略已切换: {strategy_names.get(strategy, strategy)}")
    
    def _on_priority_changed(self, priority_list: list) -> None:
        """优先级变更处理"""
        self.automator.set_priority_list(priority_list)
        self.log_viewer.add_log(f"优先级列表已更新，共 {len(priority_list)} 个卡牌")
    
    def _on_settings_changed(self, settings: dict) -> None:
        """设置变更处理"""
        if 'detect_interval' in settings:
            self.automator.set_detect_interval(settings['detect_interval'])
        if 'pick_cooldown' in settings:
            self.automator.set_pick_cooldown(settings['pick_cooldown'])
        
        self.log_viewer.add_log("设置已更新")
    
    def _update_display(self) -> None:
        """更新显示"""
        if self.automator:
            stats = self.automator.get_statistics()
            
            self.phase_label.setText(stats.get('game_phase', '未知'))
            self.card_count_label.setText(str(stats.get('recognized_cards', 0)))
            self.pick_count_label.setText(str(stats.get('current_session_picks', 0)))
            
            cards = self.automator.game_state.available_cards
            self._update_card_display(cards)
    
    def _update_card_display(self, cards: list) -> None:
        """更新卡牌显示"""
        if not cards:
            self.card_preview.setText("暂无卡牌")
            return
        
        card_text = " | ".join([card.name for card in cards[:5]])
        if len(cards) > 5:
            card_text += f" ... (+{len(cards) - 5}张)"
        
        self.card_preview.setText(card_text)
    
    def _quit_application(self) -> None:
        """退出应用程序"""
        self.automator.stop_auto_picker()
        self.automator.release()
        self.close()
    
    def closeEvent(self, event) -> None:
        """关闭事件"""
        if self.settings.get('general', 'minimize_to_tray', True):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "提示",
                "程序已最小化到系统托盘",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self._quit_application()
    
    def showEvent(self, event) -> None:
        """显示事件"""
        self._apply_settings()


from modules.image_recognition.screen_capture import ScreenCapture
