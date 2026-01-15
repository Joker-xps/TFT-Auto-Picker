# -*- coding: utf-8 -*-
"""
选牌策略单元测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.strategy import (StrategyManager, PriorityStrategy, 
                          CostBalanceStrategy, CompBuildingStrategy)
from core.card import Card
from core.game_state import GameState, GamePhase


class StrategyTestCase(unittest.TestCase):
    """选牌策略测试用例"""
    
    def setUp(self):
        """测试前置条件"""
        self.game_state = GameState()
        self.game_state.set_shop_phase()
        
        self.cards = [
            Card(name="德莱文", cost=4, confidence=0.95),
            Card(name="亚索", cost=3, confidence=0.90),
            Card(name="凯尔", cost=5, confidence=0.85),
            Card(name="盖伦", cost=1, confidence=0.80),
            Card(name="赵信", cost=2, confidence=0.75)
        ]
    
    def test_priority_strategy_creation(self):
        """测试优先级策略创建"""
        strategy = PriorityStrategy(priority_list=["卡牌1", "卡牌2"])
        self.assertEqual(strategy.get_name(), "优先级策略")
        self.assertIsNotNone(strategy.get_description())
    
    def test_priority_strategy_selection(self):
        """测试优先级策略选牌"""
        priority_list = ["亚索", "德莱文", "凯尔"]
        strategy = PriorityStrategy(priority_list=priority_list)
        
        selected = strategy.select_card(self.cards, self.game_state)
        
        self.assertIsNotNone(selected)
        self.assertEqual(selected.name, "亚索")
    
    def test_priority_strategy_set_list(self):
        """测试设置优先级列表"""
        strategy = PriorityStrategy()
        strategy.set_priority_list(["卡牌A", "卡牌B"])
        
        self.assertEqual(len(strategy.priority_list), 2)
    
    def test_priority_strategy_no_match(self):
        """测试优先级策略无匹配"""
        priority_list = ["不存在的卡牌"]
        strategy = PriorityStrategy(priority_list=priority_list)
        
        selected = strategy.select_card(self.cards, self.game_state)
        self.assertIsNone(selected)
    
    def test_priority_strategy_max_cost(self):
        """测试优先级策略费用限制"""
        priority_list = ["凯尔", "德莱文"]
        strategy = PriorityStrategy(priority_list=priority_list, max_cost=3)
        
        selected = strategy.select_card(self.cards, self.game_state)
        
        self.assertIsNotNone(selected)
        self.assertLessEqual(selected.cost, 3)
    
    def test_cost_balance_strategy(self):
        """测试费用平衡策略"""
        strategy = CostBalanceStrategy(cost_weights={5: 2.0, 4: 1.5})
        
        selected = strategy.select_card(self.cards, self.game_state)
        
        self.assertIsNotNone(selected)
    
    def test_comp_building_strategy(self):
        """测试阵容构建策略"""
        target_comp = ["德莱文", "亚索"]
        strategy = CompBuildingStrategy(target_comp=target_comp)
        
        selected = strategy.select_card(self.cards, self.game_state)
        
        self.assertIsNotNone(selected)
        self.assertIn(selected.name, target_comp)
    
    def test_strategy_manager_creation(self):
        """测试策略管理器创建"""
        manager = StrategyManager()
        
        strategies = manager.get_available_strategies()
        self.assertIn("priority", strategies)
        self.assertIn("cost_balance", strategies)
        self.assertIn("comp_building", strategies)
    
    def test_strategy_manager_set_strategy(self):
        """测试策略管理器设置策略"""
        manager = StrategyManager()
        
        result = manager.set_strategy("cost_balance")
        self.assertTrue(result)
        self.assertEqual(manager.current_strategy_name, "cost_balance")
    
    def test_strategy_manager_set_invalid_strategy(self):
        """测试策略管理器设置无效策略"""
        manager = StrategyManager()
        
        result = manager.set_strategy("invalid_strategy")
        self.assertFalse(result)
    
    def test_strategy_manager_execute_selection(self):
        """测试策略管理器执行选牌"""
        manager = StrategyManager()
        manager.set_strategy("priority")
        
        selected = manager.execute_selection(self.cards, self.game_state)
        
        self.assertIsNotNone(selected)
    
    def test_strategy_manager_get_strategy_info(self):
        """测试获取策略信息"""
        manager = StrategyManager()
        
        info = manager.get_strategy_info("priority")
        
        self.assertIsNotNone(info)
        self.assertIn('name', info)
        self.assertIn('description', info)


if __name__ == '__main__':
    unittest.main()
