# -*- coding: utf-8 -*-
"""
金铲铲之战自动拿牌工具 - 主程序入口

功能特性:
- 卡牌自动识别与抓取
- 可配置的选牌策略
- 直观的图形用户界面
- 完整的日志记录系统
- 高度模块化设计

使用方法:
    python main.py

作者: AutoDev Team
版本: 1.0.0
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt


def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        log_dir: 日志目录
        log_level: 日志级别
        
    Returns:
        Logger: 配置好的日志器
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'app_{timestamp}.log')
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成")
    logger.info(f"日志文件: {log_file}")
    
    return logger


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数
    
    Returns:
        Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='金铲铲之战自动拿牌工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py                    # 正常运行
    python main.py --debug            # 调试模式运行
    python main.py --no-tray          # 不使用系统托盘
    python main.py --min-interval 0.2 # 设置最小检测间隔
        """
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--no-tray',
        action='store_true',
        help='禁用系统托盘'
    )
    
    parser.add_argument(
        '--min-interval',
        type=float,
        default=0.1,
        help='最小检测间隔（秒），默认0.1'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别'
    )
    
    return parser.parse_args()


def main():
    """
    主函数
    """
    args = parse_arguments()
    
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    if args.debug:
        log_level = logging.DEBUG
    
    logger = setup_logging(log_level=log_level)
    logger.info("=" * 60)
    logger.info("金铲铲之战自动拿牌工具 v1.0.0")
    logger.info("=" * 60)
    
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"操作系统: {sys.platform}")
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("TFT Auto Picker")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(False)
    
    from modules.ui.main_window import MainWindow
    
    try:
        window = MainWindow()
        
        if args.debug:
            window.show()
        else:
            window.showMinimized()
        
        logger.info("应用程序启动成功")
        
        exit_code = app.exec_()
        
        logger.info(f"应用程序退出，退出码: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.exception(f"应用程序发生错误: {e}")
        QMessageBox.critical(
            None, 
            "错误", 
            f"应用程序发生错误:\n{str(e)}\n\n请查看日志文件获取详细信息。"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
