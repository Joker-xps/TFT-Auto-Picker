# -*- coding: utf-8 -*-
"""
测试模块初始化文件
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def suite():
    """加载所有测试用例"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    from tests.test_card import CardTestCase
    from tests.test_game_state import GameStateTestCase
    from tests.test_strategy import StrategyTestCase
    
    suite.addTests(loader.loadTestsFromTestCase(CardTestCase))
    suite.addTests(loader.loadTestsFromTestCase(GameStateTestCase))
    suite.addTests(loader.loadTestsFromTestCase(StrategyTestCase))
    
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
